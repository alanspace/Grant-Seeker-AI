"""
Grant Seeker Agent - Refactored to use direct Tavily API instead of MCP tools
This version should be more stable and avoid the 500 INTERNAL errors
"""
import os
import asyncio
import json
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google import genai
from google.genai import types
from pydantic import BaseModel
from tavily_client import TavilyClient

# Load environment variables
load_dotenv()
load_dotenv("../.env")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

MODEL_NAME = "gemini-flash-latest"

# Eligibility requirements for your organization
ELIGIBILITY_REQUIREMENTS = {
    "tax_exempt_status": True,  # Must be 501(c)(3)
    "purpose_or_need": True,     # Must demonstrate need
    "financial_statements": True, # Must provide financials
    "deficit_explanation": True   # Must explain any deficits
}

# Configure retry options
retry_config = types.HttpRetryOptions(
    attempts=2,
    exp_base=2,
    initial_delay=1.0,
    http_status_codes=[429, 500, 503, 504],
)

# Initialize Tavily client
tavily = TavilyClient(api_key=TAVILY_API_KEY, max_retries=3, timeout=30.0)

# Pydantic schemas
class DiscoveredLead(BaseModel):
    url: str
    source: str
    title: str = ""

class DiscoveredLeadsReport(BaseModel):
    discovered_leads: list[DiscoveredLead]

class GrantData(BaseModel):
    url: str
    budget: str = "Not specified"
    deadline: str = "Not specified"
    eligibility: str = "Not specified"

# Agents without MCP tools
finder_agent = LlmAgent(
    name="GrantFinder",
    model=Gemini(model=MODEL_NAME, retry_options=retry_config),
    instruction="""
    You are a Grant Scout. You will receive search results from Tavily.
    Your job is to analyze these results and identify the top 3-5 most promising grant opportunities.
    
    Return a JSON object with a 'discovered_leads' list.
    Each lead must have:
    - 'url': the URL of the grant page
    - 'source': the name of the organization
    - 'title': the grant title or program name
    
    Focus on official funder pages and active grant programs.
    
    Example format:
    {
      "discovered_leads": [
        {"url": "https://example.com/grant", "source": "Example Foundation", "title": "Community Grant"}
      ]
    }
    """
)

extractor_agent = LlmAgent(
    name="GrantExtractor",
    model=Gemini(model=MODEL_NAME, retry_options=retry_config),
    instruction=f"""
    You are a Data Extractor. You will receive the content of a grant webpage.
    
    Extract the following information:
    1. Budget/Funding Amount
    2. Application Deadline
    3. Eligibility Requirements (full text)
    4. Check if the grant mentions these specific requirements:
       - Tax-exempt status (501(c)(3) or non-profit status)
       - Purpose or demonstrated need statement
       - Financial statements or budget documents
       - Deficit explanation or financial justification
    
    IMPORTANT: Calculate match_score based on how many requirements are mentioned:
    - If ALL 4 requirements are mentioned: match_score = 100
    - If 3 requirements are mentioned: match_score = 75
    - If 2 requirements are mentioned: match_score = 50
    - If 1 requirement is mentioned: match_score = 25
    - If 0 requirements are mentioned: match_score = 0
    
    Even if the page doesn't explicitly list all requirements, if it mentions non-profit eligibility,
    that usually implies tax-exempt status and basic documentation needs.
    
    Return a JSON object with these fields:
    - url: the URL provided
    - budget: funding amount or "Not specified"
    - deadline: application deadline or "Not specified"
    - eligibility: full eligibility requirements text
    - requires_tax_exempt: true if mentions 501(c)(3), non-profit, or tax-exempt, false otherwise
    - requires_purpose: true if mentions purpose, need, or project description, false otherwise
    - requires_financials: true if mentions financial statements, budget, or IRS 990, false otherwise
    - requires_deficit_explanation: true if mentions deficit, financial justification, or explanation, false otherwise
    - match_score: number 0-100 based on how many requirements match (see formula above)
    
    Be generous in your interpretation - if a grant is for non-profits, assume it requires tax-exempt status.
    
    Example format:
    {{
      "url": "https://example.com/grant",
      "budget": "$50,000",
      "deadline": "March 15, 2024",
      "eligibility": "Non-profit organizations in Chicago with 501(c)(3) status must submit a project proposal and budget",
      "requires_tax_exempt": true,
      "requires_purpose": true,
      "requires_financials": true,
      "requires_deficit_explanation": false,
      "match_score": 75
    }}
    """
)


async def main():
    print(f"🚀 Starting Grant Seeker Workflow (Direct Tavily API with {MODEL_NAME})...")
    
    # Initialize Session Service
    session_service = InMemorySessionService()
    
    # Create the session
    await session_service.create_session(
        app_name="grant_seeker_direct",
        user_id="console_user",
        session_id="main_session"
    )

    # --- PHASE 1: SEARCH FOR GRANTS ---
    print("\n🔎 Phase 1: Searching for Grants...")
    query = "community garden grants for urban youth in Chicago"
    
    # Use Tavily wrapper
    search_results = await tavily.search(query, max_results=5)
    print(f"✅ Found {len(search_results)} search results")
    
    if not search_results:
        print("❌ No search results found. Exiting.")
        return
    
    # Format search results for the agent
    search_summary = "Here are the search results:\n\n"
    for i, result in enumerate(search_results, 1):
        search_summary += f"{i}. {result.get('title', 'No title')}\n"
        search_summary += f"   URL: {result.get('url', '')}\n"
        search_summary += f"   Snippet: {result.get('content', '')[:200]}...\n\n"
    
    # Ask the finder agent to analyze results
    finder_runner = Runner(
        agent=finder_agent,
        app_name="grant_seeker_direct",
        session_service=session_service
    )
    
    user_msg = types.Content(role="user", parts=[types.Part(text=search_summary)])
    
    leads_json_str = ""
    async for event in finder_runner.run_async(
        user_id="console_user",
        session_id="main_session",
        new_message=user_msg
    ):
        if event.is_final_response() and event.content and event.content.parts:
            leads_json_str = event.content.parts[0].text

    # Parse the leads
    try:
        clean_json = leads_json_str.replace("```json", "").replace("```", "").strip()
        leads_data = json.loads(clean_json)
        
        if isinstance(leads_data, dict) and "discovered_leads" in leads_data:
            leads = leads_data["discovered_leads"]
        elif isinstance(leads_data, list):
            leads = leads_data
        else:
            leads = []
    except Exception as e:
        print(f"❌ Error parsing leads: {e}")
        print(f"Raw output: {leads_json_str}")
        return

    print(f"✅ Identified {len(leads)} promising grants")

    # --- PHASE 2: EXTRACT DATA FROM EACH GRANT ---
    print(f"\n📊 Phase 2: Extracting Data (Sequential Processing)...")
    
    # Semaphore to limit concurrency
    sem = asyncio.Semaphore(1)

    async def process_single_url(lead):
        async with sem:
            url = lead.get('url')
            print(f"   -> ⏳ Extracting: {url}")
            
            # Get page content using Tavily wrapper
            content = await tavily.get_page_content(url)
            
            if not content:
                print(f"   -> ⚠️ Could not fetch content for: {url}")
                # Return consistent JSON format
                return {
                    "url": url,
                    "budget": "Not specified",
                    "deadline": "Not specified",
                    "eligibility": "Not specified",
                    "error": "Could not fetch content"
                }
            
            # Create unique session for this extraction
            task_session_id = f"extract_{hash(url)}"
            await session_service.create_session(
                app_name="grant_seeker_direct",
                user_id="console_user",
                session_id=task_session_id
            )

            extractor_runner = Runner(
                agent=extractor_agent,
                app_name="grant_seeker_direct",
                session_service=session_service
            )
            
            # Pass the content to the extractor
            content_preview = content[:2000]  # Limit to first 2000 chars
            msg = types.Content(
                role="user", 
                parts=[types.Part(text=f"URL: {url}\n\nContent:\n{content_preview}")]
            )
            
            result_text = ""
            try:
                async for event in extractor_runner.run_async(
                    user_id="console_user",
                    session_id=task_session_id,
                    new_message=msg
                ):
                    if event.is_final_response() and event.content and event.content.parts:
                        result_text = event.content.parts[0].text
                
                # Parse and validate the JSON response
                clean_json = result_text.replace("```json", "").replace("```", "").strip()
                grant_data = json.loads(clean_json)
                
                # Ensure all required fields exist
                return {
                    "url": url,
                    "budget": grant_data.get("budget", "Not specified"),
                    "deadline": grant_data.get("deadline", "Not specified"),
                    "eligibility": grant_data.get("eligibility", "Not specified"),
                    "requires_tax_exempt": grant_data.get("requires_tax_exempt", False),
                    "requires_purpose": grant_data.get("requires_purpose", False),
                    "requires_financials": grant_data.get("requires_financials", False),
                    "requires_deficit_explanation": grant_data.get("requires_deficit_explanation", False),
                    "match_score": grant_data.get("match_score", 0)
                }
                
            except json.JSONDecodeError as e:
                print(f"   -> ⚠️ JSON parse error for {url}: {e}")
                return {
                    "url": url,
                    "budget": "Not specified",
                    "deadline": "Not specified",
                    "eligibility": "Not specified",
                    "error": f"JSON parse error: {str(e)}"
                }
            except Exception as e:
                print(f"   -> ⚠️ Extraction error for {url}: {e}")
                return {
                    "url": url,
                    "budget": "Not specified",
                    "deadline": "Not specified",
                    "eligibility": "Not specified",
                    "error": str(e)
                }
            finally:
                print(f"   -> ✅ Finished: {url}")

    # Process all URLs
    tasks = [process_single_url(lead) for lead in leads]
    results = await asyncio.gather(*tasks)

    # Sort by match_score (highest first)
    sorted_results = sorted(
        results, 
        key=lambda x: x.get('match_score', 0), 
        reverse=True
    )

    print("\n✅ Workflow Complete!")
    print("\n" + "="*60)
    print("FINAL RESULTS (Sorted by Match Score)")
    print("="*60)
    
    # Print results in a clean, consistent format
    for i, grant in enumerate(sorted_results, 1):
        match_score = grant.get('match_score', 0)
        
        # Color code based on match score
        if match_score >= 75:
            match_indicator = "🟢 EXCELLENT MATCH"
        elif match_score >= 50:
            match_indicator = "🟡 GOOD MATCH"
        elif match_score >= 25:
            match_indicator = "🟠 PARTIAL MATCH"
        else:
            match_indicator = "🔴 POOR MATCH"
        
        print(f"\n--- Grant {i} --- {match_indicator} ({match_score}%)")
        print(f"URL: {grant['url']}")
        print(f"Budget: {grant.get('budget', 'Not specified')}")
        print(f"Deadline: {grant.get('deadline', 'Not specified')}")
        print(f"Eligibility: {grant.get('eligibility', 'Not specified')}")
        
        # Show requirement matches
        if grant.get('requires_tax_exempt') is not None:
            print(f"\nRequirement Matches:")
            print(f"  {'✅' if grant.get('requires_tax_exempt') else '❌'} Tax-Exempt Status")
            print(f"  {'✅' if grant.get('requires_purpose') else '❌'} Purpose/Need Statement")
            print(f"  {'✅' if grant.get('requires_financials') else '❌'} Financial Statements")
            print(f"  {'✅' if grant.get('requires_deficit_explanation') else '❌'} Deficit Explanation")
        
        if 'error' in grant:
            print(f"⚠️  Error: {grant['error']}")

if __name__ == "__main__":
    asyncio.run(main())
