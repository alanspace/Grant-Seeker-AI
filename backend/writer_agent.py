# import os
# from dotenv import load_dotenv
# import google.generativeai as genai

# # Load environment variables from .env file
# load_dotenv()

# def draft_proposal_section(project_details, grant_requirements):
#     """
#     Drafts a section of a grant proposal using the Gemini model.

#     Args:
#         project_details (str): Details about the project.
#         grant_requirements (str): Specific requirements for the grant section.

#     Returns:
#         str: The generated proposal section text.
#     """
    
#     # Retrieve GEMINI_API_KEY from environment variables
#     GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

#     if not GEMINI_API_KEY:
#         print("Error: GEMINI_API_KEY not found in .env file.")
#         return ""

#     # Configure the Gemini API
#     # We need to configure the library with the API key to authenticate our requests.
#     genai.configure(api_key=GEMINI_API_KEY)

#     # Initialize the model
#     # We use 'gemini-pro' (or a similar available model) for text generation.
#     # model = genai.GenerativeModel('gemini-pro')
#     # model = genai.GenerativeModel('gemini-pro-latest')
#     model = genai.GenerativeModel('gemini-flash-latest')
#     # Construct the prompt
#     # Prompt engineering is crucial here. We instruct the model to adopt a specific persona 
#     # (professional grant writer) and provide clear context (project details) and a specific goal (grant requirements).
#     prompt = f"""
#     You are an expert professional grant writer with a track record of securing funding for non-profit projects.
    
#     Your task is to write a specific section of a grant proposal based on the following information:
    
#     PROJECT DETAILS:
#     {project_details}
    
#     SECTION REQUIREMENTS:
#     {grant_requirements}
    
#     Please write a compelling, well-structured, and persuasive response that directly addresses the requirements using the project details provided. 
#     Ensure the tone is professional, inspiring, and aligned with standard grant writing practices.
#     """

#     try:
#         # Generate content
#         # We send the prompt to the model to generate the response.
#         response = model.generate_content(prompt)

#         # Return the text
#         # We extract the text from the response object.
#         return response.text
#     except Exception as e:
#    puts you will receive:
#     1. Project Description (What we want to do)
#     2. Grant Details (The constraints found by the researcher: Budget, Deadline, Eligibility)
    
#     Guidelines:
#     - Tone: Professional, persuasive, and urgent.
#     - Use the 'Eligibility' data to explicitly state why we qualify.
#     - Use the 'Budget' data to frame the request (don't ask for too much).
#     - Mention the 'Deadline' in the internal notes if it's soon.
#     - Structure: Use Markdown headers (##).
    
#     Do not hallucinate facts. Use the provided project details.
#     """
# )     print(f"An error occurred during generation: {e}")
# #         print("Falling back to mock proposal text for demonstration purposes.")
# #         return f"""
#         [MOCK PROPOSAL SECTION]
        
#         Project Title: {project_details[:50]}...
        
#         Response to Requirements:
#         Our community garden initiative directly addresses the grant's mission by transforming underutilized urban spaces into vibrant hubs of food production and education. By providing fresh, organic produce to food deserts in Chicago, we tackle food insecurity head-on. Furthermore, our educational workshops empower local youth with sustainable gardening skills, fostering a new generation of environmental stewards. This project aligns perfectly with your goal of supporting community-led sustainable agriculture and health initiatives.
#         """

# if __name__ == "__main__":
#     # Example usage
#     details = "A community garden project in downtown aiming to provide fresh produce to low-income families and educational workshops for youth."
#     reqs = "Describe the impact of your project on the local community."
#     proposal_text = draft_proposal_section(details, reqs)
#     print("Drafted Proposal Section:")
#     print(proposal_text)
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