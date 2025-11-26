"""
Grant Seeker Agent - Refactored to use direct Tavily API instead of MCP tools
This version should be more stable and avoid the 500 INTERNAL errors
"""
import os
import asyncio
import json
from datetime import datetime
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from pydantic import BaseModel
from tavily_client import TavilyClient

# Load environment variables
load_dotenv()
load_dotenv("../.env")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Model configuration
MODEL_NAME = "gemini-flash-latest"

# Configure retry options
retry_config = types.HttpRetryOptions(
    attempts=1,
    exp_base=2,
    initial_delay=1.0,
    http_status_codes=[429, 500, 503, 504],
)

# Initialize Tavily client
tavily = TavilyClient(api_key=TAVILY_API_KEY, max_retries=2, timeout=15.0)

# Get current date for context
CURRENT_DATE = datetime.now().strftime("%B %d, %Y")
CURRENT_DATE_ISO = datetime.now().strftime("%Y-%m-%d")

# Pydantic schemas
class DiscoveredLead(BaseModel):
    url: str
    source: str
    title: str = ""

class DiscoveredLeadsReport(BaseModel):
    discovered_leads: list[DiscoveredLead]

class GrantData(BaseModel):
    id: int = 0
    title: str = "Untitled Grant"
    funder: str = "Unknown"
    deadline: str = "Not specified"
    amount: str = "Not specified"
    description: str = "No description available"
    detailed_overview: str = "No detailed overview available"
    tags: list[str] = []
    eligibility: str = "Not specified"
    url: str = ""
    application_requirements: list[str] = []
    funding_type: str = "Grant"
    geography: str = "Not specified"

# Agents
finder_agent = LlmAgent(
    name="GrantFinder",
    model=Gemini(model=MODEL_NAME, retry_options=retry_config),
    instruction="""
    You are a Grant Scout. You will receive search results from Tavily.
    Your job is to analyze these results and identify the top 5-7 most promising grant opportunities.
    
    Return a JSON object with a 'discovered_leads' list.
    Each lead must have:
    - 'url': the URL of the grant page
    - 'source': the name of the organization
    - 'title': the grant title or program name
    
    Focus on official funder pages and active grant programs, NOT grant directories or lists.
    
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

    IMPORTANT - CURRENT DATE CONTEXT:
    Today's date is: {CURRENT_DATE} ({CURRENT_DATE_ISO})
    Only extract grants with deadlines in the FUTURE (after {CURRENT_DATE_ISO}).
    If a deadline has already passed, note it but mark as expired.
    
    Extract the following information and return as a JSON object:
    
    Required fields:
    - title: The grant program name/title
    - funder: The organization or foundation offering the grant
    - deadline: Application deadline date (BE THOROUGH - look for ANY dates, cycles, rounds)
    - amount: Funding amount (BE THOROUGH - look for $, ranges, "up to", award amounts)
    - description: Brief 1-2 sentence summary of what the grant funds
    - detailed_overview: Comprehensive description of the grant program, goals, and purpose
    - tags: Array of relevant category tags (e.g., ["Education", "Youth", "Community"])
    - eligibility: Full eligibility requirements text
    - url: The URL provided
    - application_requirements: Array of application requirements (e.g., ["501(c)(3) status", "Program budget"])
    - funding_type: Type of funding (default to "Grant")
    - geography: Geographic scope or location requirements (e.g., "Chicago", "Illinois", "United States")
    
    CRITICAL - Deadline & Amount Extraction:
    - deadline: Search ENTIRE page for dates! Look for "deadline", "due", "apply by", "submit by", grant cycles, fiscal years
      * If you find "rolling" or "ongoing", use "Rolling deadline"
      * If multiple cycles, list the NEXT upcoming date AFTER {CURRENT_DATE_ISO}
      * Format as YYYY-MM-DD if possible
      * If deadline is BEFORE {CURRENT_DATE_ISO}, use "Expired (YYYY-MM-DD)"
    - amount: Search ENTIRE page for dollar signs, numbers, ranges!
      * Look in titles, headings, tables, fine print
      * If you see "up to $X", use exactly "Up to $X"
      * If range "$5,000-$25,000", format as "$5,000 - $25,000"
    
    Other requirements:
    - Extract actual data from the page content
    - If truly not found after thorough search, use defaults
    - Be thorough with detailed_overview
    - Generate 3-5 relevant tags based on content
    
    Example format:
    {{
      "title": "Community Garden Grant Program",
      "funder": "Green Cities Foundation",
      "deadline": "2026-05-15",
      "amount": "$1,000 - $5,000",
      "description": "Funding for urban community gardens that serve youth populations.",
      "detailed_overview": "The Community Garden Grant Program supports urban gardens...",
      "tags": ["Community", "Gardens", "Youth", "Urban"],
      "eligibility": "501(c)(3) non-profit organizations serving Chicago communities",
      "url": "https://example.com/grant",
      "application_requirements": ["501(c)(3) status", "Project budget", "Site plan"],
      "funding_type": "Grant",
      "geography": "Chicago, Illinois"
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
    # Improved query - more specific, includes key terms for finding complete grant info
    query = "community garden grants Chicago 2025 deadline application amount funding active open"
    
    # Get 5 results for faster processing
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
    print(f"\n📊 Phase 2: Extracting Data (Parallel Processing - 3 at a time)...")
    
    # Semaphore to limit concurrency (3 parallel grants)
    sem = asyncio.Semaphore(3)

    async def process_single_url(lead):
        async with sem:
            url = lead.get('url')
            print(f"   -> ⏳ Extracting: {url}")
            
            # Get page content using Tavily wrapper
            content = await tavily.get_page_content(url)
            
            if not content:
                print(f"   -> ⚠️ Could not fetch content for: {url}")
                return {
                    "id": 0,
                    "title": "Untitled Grant",
                    "funder": "Unknown",
                    "deadline": "Not specified",
                    "amount": "Not specified",
                    "description": "No description available",
                    "detailed_overview": "No detailed overview available",
                    "tags": [],
                    "eligibility": "Not specified",
                    "url": url,
                    "application_requirements": [],
                    "funding_type": "Grant",
                    "geography": "Not specified",
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
            
            # Pass optimized content to the extractor (3000 chars for speed)
            content_preview = content[:3000]
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
                
                # Helper function to normalize empty values
                def normalize_value(value, default):
                    """Convert empty strings, None, or whitespace-only strings to default value"""
                    if value is None or (isinstance(value, str) and not value.strip()):
                        return default
                    return value
                
                # Ensure all required fields exist with frontend-compatible structure
                return {
                    "id": grant_data.get("id", 0),
                    "title": normalize_value(grant_data.get("title"), "Untitled Grant"),
                    "funder": normalize_value(grant_data.get("funder"), "Unknown"),
                    "deadline": normalize_value(grant_data.get("deadline"), "Not specified"),
                    "amount": normalize_value(grant_data.get("amount"), "Not specified"),
                    "description": normalize_value(grant_data.get("description"), "No description available"),
                    "detailed_overview": normalize_value(grant_data.get("detailed_overview"), "No detailed overview available"),
                    "tags": grant_data.get("tags", []) if grant_data.get("tags") else [],
                    "eligibility": normalize_value(grant_data.get("eligibility"), "Not specified"),
                    "url": url,
                    "application_requirements": grant_data.get("application_requirements", []) if grant_data.get("application_requirements") else [],
                    "funding_type": normalize_value(grant_data.get("funding_type"), "Grant"),
                    "geography": normalize_value(grant_data.get("geography"), "Not specified")
                }
                
            except json.JSONDecodeError as e:
                print(f"   -> ⚠️ JSON parse error for {url}: {e}")
                return {
                    "id": 0,
                    "title": "Untitled Grant",
                    "funder": "Unknown",
                    "deadline": "Not specified",
                    "amount": "Not specified",
                    "description": "No description available",
                    "detailed_overview": "No detailed overview available",
                    "tags": [],
                    "eligibility": "Not specified",
                    "url": url,
                    "application_requirements": [],
                    "funding_type": "Grant",
                    "geography": "Not specified",
                    "error": f"JSON parse error: {str(e)}"
                }
            except Exception as e:
                print(f"   -> ⚠️ Extraction error for {url}: {e}")
                return {
                    "id": 0,
                    "title": "Untitled Grant",
                    "funder": "Unknown",
                    "deadline": "Not specified",
                    "amount": "Not specified",
                    "description": "No description available",
                    "detailed_overview": "No detailed overview available",
                    "tags": [],
                    "eligibility": "Not specified",
                    "url": url,
                    "application_requirements": [],
                    "funding_type": "Grant",
                    "geography": "Not specified",
                    "error": str(e)
                }
            finally:
                print(f"   -> ✅ Finished: {url}")

    # Process all URLs
    tasks = [process_single_url(lead) for lead in leads]
    results = await asyncio.gather(*tasks)

    # Assign IDs to each grant
    for i, grant in enumerate(results, 1):
        grant['id'] = i

    # Save results as JSON file for frontend
    output_file = "grants_output.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Workflow Complete!")
    print(f"📄 JSON output saved to: {output_file}")
    print("\n" + "="*80)
    print("FINAL RESULTS")
    print("="*80)
    
    # Print results in a clean, frontend-compatible format
    for grant in results:
        print(f"\n{'='*80}")
        print(f"Grant #{grant['id']}: {grant.get('title', 'Untitled Grant')}")
        print(f"{'='*80}")
        print(f"Funder: {grant.get('funder', 'Unknown')}")
        print(f"Amount: {grant.get('amount', 'Not specified')}")
        print(f"Deadline: {grant.get('deadline', 'Not specified')}")
        print(f"Geography: {grant.get('geography', 'Not specified')}")
        print(f"Funding Type: {grant.get('funding_type', 'Grant')}")
        print(f"\nDescription:")
        print(f"  {grant.get('description', 'No description available')}")
        print(f"\nDetailed Overview:")
        print(f"  {grant.get('detailed_overview', 'No detailed overview available')}")
        print(f"\nEligibility:")
        print(f"  {grant.get('eligibility', 'Not specified')}")
        
        # Show tags
        tags = grant.get('tags', [])
        if tags:
            print(f"\nTags: {', '.join(tags)}")
        
        # Show application requirements
        app_reqs = grant.get('application_requirements', [])
        if app_reqs:
            print(f"\nApplication Requirements:")
            for req in app_reqs:
                print(f"  • {req}")
        
        print(f"\nURL: {grant['url']}")
        
        if 'error' in grant:
            print(f"\n⚠️  Error: {grant['error']}")
    
    # Return results for API/programmatic use
    return results

if __name__ == "__main__":
    asyncio.run(main())
