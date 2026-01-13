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
from backend.adk_agent import GrantSeekerWorkflow
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
    print(f"API: Running Grant Seeker Workflow for: '{project_description}'")

    # Helper to run async workflow
    async def _run_workflow():
        workflow = GrantSeekerWorkflow()
        return await workflow.run(project_description)

    # Run the async helper
    try:
        return asyncio.run(_run_workflow())
    except Exception as e:
        print(f"API ERROR: Workflow failed. Error: {e}")
        return [{"error": f"The workflow encountered an error: {str(e)}"}]


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