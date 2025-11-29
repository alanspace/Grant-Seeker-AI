# api.py
# This is the ONLY file the frontend (app.py) should import.
# It acts as a clean bridge to our powerful backend agents.

import asyncio
import json
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import uuid
# Import our two main agent engines
from backend.adk_agent import root_agent as tavily_agent
from backend.writer_agent import draft_proposal_section as run_writer_agent

# Load environment variables once at the start
load_dotenv()

# --- API FUNCTION 1: FIND & ANALYZE GRANTS ---
def find_and_analyze_grants(project_description: str) -> list[dict]:
    """
    Called by the UI when the user clicks "Find Grants".
    This function runs the entire Tavily multi-agent workflow.
    Returns a clean LIST of grant dictionaries.
    """
    print(f"API: Running Tavily Sequential Agent for: '{project_description}'")

    # We need a helper to run our async ADK code from a sync function
    async def _run_tavily_workflow():
        session_service = InMemorySessionService()
        session_id = f"tavily_session_{int(time.time() * 1000)}"
        await session_service.create_session(
            app_name="tavily_app",
            user_id="ui_user",
            session_id=session_id
        )
        runner = Runner(
            agent=tavily_agent,
            app_name="tavily_app",
            session_service=session_service
        )
        user_msg = types.Content(role="user", parts=[types.Part(text=project_description)])

        # Run the async stream and capture the final text result
        final_text = ""
        async for event in runner.run_async(
            user_id="ui_user",
            session_id=session_id,
            new_message=user_msg
        ):
            if event.is_final_response() and event.content and event.content.parts:
                final_text = event.content.parts[0].text
        return final_text

    # Run the async helper
    raw_json_string = asyncio.run(_run_tavily_workflow())

    # --- PARSE THE OUTPUT ---
    # The agent returns a string that looks like JSON. We must parse it.
    try:
        # The LLM might wrap the JSON in ```json ... ```. We remove that.
        clean_json_string = raw_json_string.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_json_string)

        # Based on the Pydantic schema, the key should be 'found_grants'
        if "found_grants" in data:
            return data["found_grants"]
        else:
            print("API WARNING: Agent ran but did not return 'found_grants' key.")
            return []
            
    except (json.JSONDecodeError, TypeError) as e:
        print(f"API ERROR: Could not parse agent's final output as JSON. Error: {e}")
        print(f"--- Raw Agent Output --- \n{raw_json_string}\n--------------------")
        return [{"error": "The AI agent returned a non-JSON response. Please try rephrasing your query."}]


# --- API FUNCTION 2: DRAFT THE PROPOSAL ---
def draft_proposal(project_description: str, selected_grant_dict: dict) -> str:
    """
    Called by the UI when the user clicks "Draft Proposal" on a specific grant.
    This function calls our Writer Agent.
    """
    print("API: Calling Writer Agent...")
    if not isinstance(selected_grant_dict, dict):
        return "Error: Invalid grant data provided to the writer."
        
    return run_writer_agent(project_description, selected_grant_dict)


# --- Test Block (for running `python api.py` directly) ---
if __name__ == "__main__":
    print("--- [STARTING API.PY TEST] ---")
    
    # 1. Test the grant finding and analysis
    test_query = "Find community garden grants for non-profits"
    found_grants = find_and_analyze_grants(test_query)
    
    print(f"\n✅ Found {len(found_grants)} grants.")
    
    if found_grants:
        # 2. Test the proposal drafting with the first result
        print("\n--- Testing Writer with the first grant found ---")
        first_grant = found_grants[0]
        proposal = draft_proposal(test_query, first_grant)
        
        print("\n--- Final Proposal Draft (Sample) ---")
        print(proposal[:500] + "...")

    print("\n--- [API.PY TEST COMPLETE] ---")