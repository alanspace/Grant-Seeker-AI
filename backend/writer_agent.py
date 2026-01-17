import os
import asyncio
import uuid
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Load Env
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Validate required environment variable
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY must be set in .env file")

# Config
# Use Flash for writing (faster/cheaper) or Pro for quality. 
# Since your key supports Pro, let's use it for better writing quality.
MODEL_NAME = "gemini-flash-latest"

retry_config = types.HttpRetryOptions(
    attempts=3,
    exp_base=2,
    initial_delay=1.0,
    http_status_codes=[429, 500, 503, 504],
)

# --- The Agent Definition ---
# We define the writer as an ADK Agent. 
# It doesn't need tools; its power is in the Prompt Engineering.

# --- Agent Definition ---
# The Writer Agent is a specialized persona designed to draft grant proposals.
# It takes the project description and the specific grant details as input
# and produces a tailored "Statement of Need" and "Alignment" section.
writer_agent = LlmAgent(
    name="GrantWriter",
    model=Gemini(model=MODEL_NAME, retry_options=retry_config),
    instruction="""
    You are an expert professional Grant Writer for non-profits.
    Your Task: Write a compelling "Statement of Need" and "Alignment" section.
    
    Inputs:
    1. Project Description
    2. Grant Details (Budget, Deadline, Eligibility)
    
    Guidelines:
    - Tone: Professional, persuasive, and urgent.
    - Explicitly reference the eligibility criteria and how we meet them.
    - Mention the deadline if it is approaching.
    - Use Markdown headers.
    """
)

# --- The Interface Function ---
def draft_proposal_section(project_details: str, grant_json: dict) -> str:
    """
    Formats inputs and runs the Writer Agent.
    
    This function acts as a bridge between the synchronous Streamlit frontend
    and the asynchronous ADK backend. It prepares the prompt with all necessary context
    and executes the agent run.
    """
    
    # 1. Prepare the Prompt
    grant_context = f"""
    Target Grant: {grant_json.get('source', 'Unknown Funder')}
    URL: {grant_json.get('url')}
    Eligibility: {grant_json.get('eligibility', 'Not specified')}
    Budget: {grant_json.get('budget', 'Not specified')}
    Deadline: {grant_json.get('deadline', 'Not specified')}
    """

    prompt = f"PROJECT: {project_details}\n\nGRANT DATA: {grant_context}\n\nPlease write the proposal draft."

    # 2. Run the Agent using ADK Runner
    # We use a helper function to run async code synchronously
    async def _run_agent():
        session_service = InMemorySessionService()
        
        # Use unique session ID to avoid collision errors
        session_id = f"writer-{uuid.uuid4().hex[:12]}"
        
        # We need to create the session before running
        await session_service.create_session(
            app_name="grant_writer_app",
            user_id="writer_test_user",
            session_id=session_id
        )

        runner = Runner(
            agent=writer_agent,
            app_name="grant_writer_app",
            session_service=session_service
        )

        # Wrap the text in the correct Content object
        user_msg = types.Content(role="user", parts=[types.Part(text=prompt)])

        # Await the run_async stream to get the final result
        final_text = ""
        async for event in runner.run_async(
            user_id="writer_test_user",
            session_id=session_id,
            new_message=user_msg
        ):
            if event.is_final_response() and event.content and event.content.parts:
                final_text = event.content.parts[0].text
        
        return final_text

    return asyncio.run(_run_agent())

# --- Test Block ---
if __name__ == "__main__":
    mock_grant = {
        "source": "Test Foundation",
        "url": "http://test.com",
        "eligibility": "Must be a non-profit.",
        "budget": "$50k",
        "deadline": "2025"
    }
    print(draft_proposal_section("Community garden project", mock_grant))