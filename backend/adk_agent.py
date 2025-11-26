import os
import dotenv
import asyncio
import json
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams
from google.adk.models import Gemini
from google.genai import types
from pydantic import BaseModel, Field

# 1. Setup Environment
dotenv.load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Use the fast Flash model
MODEL_NAME = "gemini-flash-latest"

# 2. Setup Tools
tavily_mcp = McpToolset(
    connection_params=StreamableHTTPServerParams(
        url="https://mcp.tavily.com/mcp/",
        headers={"Authorization": f"Bearer {TAVILY_API_KEY}"},
    ),
)

retry_config = types.HttpRetryOptions(
    attempts=2, # Reduced from 5 to avoid long waits
    exp_base=2, # Reduced from 7 to retry faster
    initial_delay=1.0,
    http_status_codes=[429, 500, 503, 504],
)

# 3. Pydantic Schemas
class DiscoveredLead(BaseModel):
    url: str = Field(description="Direct link to the grant page or document")
    source: str = Field(description="Name of the organization or website")

class DiscoveredLeadsReport(BaseModel):
    discovered_leads: list[dict]

# 4. Agents

# --- Step 1: Finder ---
finder_agent = LlmAgent(
    name="GrantFinder",
    model=Gemini(model=MODEL_NAME, retry_options=retry_config),
    instruction="""
    You are a Grant Scout. Your job is to find active URLs for grants that match the user's brief.
    1. Use the Tavily MCP to search for *official* funder pages.
    2. Return a list of the top 3-5 most promising URLs.
    3. Format your output as a JSON object with a 'discovered_leads' list.
    4. Each lead must have 'url' and 'source'.
    Do NOT visit the detailed links yet. Just find them.
    """,
    tools=[tavily_mcp],
    output_key="discovered_leads",
    output_schema=DiscoveredLeadsReport
)

# --- Step 2: Extractor (Single URL) ---
extractor_agent = LlmAgent(
    name="GrantExtractor",
    model=Gemini(model=MODEL_NAME, retry_options=retry_config),
    instruction="""
    You are a Data Extractor. You will receive a single URL.
    
    1. Read the page content using Tavily.
    2. Extract Budget, Deadline, and Eligibility exactly as they appear.
    
    Return a final report containing all extracted data. 
    YOUR FINAL OUTPUT MUST BE ONLY A VALID JSON OBJECT with a 'found_grants' key.
    """,
    tools=[tavily_mcp],
    output_key="scout_final_report",
)

# --- 5. EXECUTION BLOCK ---
if __name__ == "__main__":
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    
    async def main():
        print(f"🚀 Starting Grant Seeker Workflow (Optimized Parallel Mode with {MODEL_NAME})...")
        
        # 1. Initialize Session Service
        session_service = InMemorySessionService()
        
        # 2. Create the session explicitly
        await session_service.create_session(
            app_name="grant_seeker_test",
            user_id="console_user",
            session_id="test_session"
        )
        
        # --- PHASE 1: FIND LEADS ---
        print("\n🔎 Phase 1: Finding Grants...")
        finder_runner = Runner(
            agent=finder_agent,
            app_name="grant_seeker_test",
            session_service=session_service
        )
        
        query = "Find community garden grants for urban youth in Chicago"
        user_msg = types.Content(role="user", parts=[types.Part(text=query)])
        
        leads_json_str = ""
        async for event in finder_runner.run_async(
            user_id="console_user",
            session_id="test_session",
            new_message=user_msg
        ):
            if event.is_final_response() and event.content and event.content.parts:
                leads_json_str = event.content.parts[0].text

        # Parse the leads
        try:
            # Clean up potential markdown code blocks
            clean_json = leads_json_str.replace("```json", "").replace("```", "").strip()
            leads_data = json.loads(clean_json)
            # Handle both list directly or dict with key
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

        print(f"✅ Found {len(leads)} potential grants. Starting parallel extraction (max 2 at a time)...")

        # --- PHASE 2: PARALLEL EXTRACTION ---
        
        # Semaphore to limit concurrency to 2 (Process 2 URLs at once)
        sem = asyncio.Semaphore(2)

        async def process_single_url(lead):
            async with sem:
                url = lead.get('url')
                print(f"   -> ⏳ Starting extraction for: {url}")
                
                # Create a unique session ID for each parallel task to avoid state conflicts
                task_session_id = f"session_{hash(url)}"
                await session_service.create_session(
                    app_name="grant_seeker_test",
                    user_id="console_user",
                    session_id=task_session_id
                )

                extractor_runner = Runner(
                    agent=extractor_agent,
                    app_name="grant_seeker_test",
                    session_service=session_service
                )
                
                # Pass the URL as the user message
                msg = types.Content(role="user", parts=[types.Part(text=f"Extract data from: {url}")])
                
                result_text = ""
                try:
                    async for event in extractor_runner.run_async(
                        user_id="console_user",
                        session_id=task_session_id,
                        new_message=msg
                    ):
                        if event.is_final_response() and event.content and event.content.parts:
                            result_text = event.content.parts[0].text
                except Exception as e:
                    result_text = f"Error extracting {url}: {str(e)}"
                    
                print(f"   -> ✅ Finished: {url}")
                return result_text

        # Launch all tasks simultaneously
        tasks = [process_single_url(lead) for lead in leads]
        results = await asyncio.gather(*tasks)

        print("\n✅ Workflow Complete!")
        print("--- Final Parallel Results ---")
        for i, res in enumerate(results):
            print(f"\n--- Result {i+1} ---")
            print(res)

    # Run the async function
    asyncio.run(main())