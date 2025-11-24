# import os
# import dotenv
# import asyncio
# from google.adk.agents import LlmAgent, SequentialAgent
# from google.adk.tools.mcp_tool.mcp_toolset import McpToolset # FIXED: Capitalization
# from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams
# from google.adk.models import Gemini
# from google.genai import types
# from pydantic import BaseModel, Field

# # 1. Setup Environment
# dotenv.load_dotenv()
# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# # CRITICAL FIX: Use the model that works for your key
# MODEL_NAME = "gemini-flash-latest" 

# # 2. Setup Tools
# tavily_mcp = McpToolset(
#     connection_params=StreamableHTTPServerParams(
#         url="https://mcp.tavily.com/mcp/",
#         headers={"Authorization": f"Bearer {TAVILY_API_KEY}"},
#     ),
# )

# retry_config = types.HttpRetryOptions(
#     attempts=5,
#     exp_base=7,
#     initial_delay=1.0,
#     http_status_codes=[429, 500, 503, 504],
# )

# # 3. Pydantic Schemas
# class DiscoveredLead(BaseModel):
#     url: str = Field(description="Direct link to the grant page or document")
#     source: str = Field(description="Name of the organization or website")

# class DiscoveredLeadsReport(BaseModel):
#     # FIXED: Changed to list[dict] to prevent ADK parsing error
#     discovered_leads: list[dict]

# class RawGrantData(BaseModel):
#     url: str
#     funder_name: str | None
#     grant_title: str | None
#     budget_text: str | None = Field(description="Verbatim budget mentions")
#     deadline_text: str | None = Field(description="Verbatim deadline mentions")
#     eligibility_text: str | None = Field(description="Raw text describing who can apply")
#     description_summary: str = Field(description="A neutral 2-sentence summary")
    
# class ScoutReport(BaseModel):
#     # FIXED: Changed to list[dict] to prevent ADK parsing error
#     found_grants: list[dict]

# # 4. Agents

# # --- Step 1: Finder ---
# finder_agent = LlmAgent(
#     name="GrantFinder",
#     model=Gemini(model=MODEL_NAME, retry_options=retry_config),
#     instruction="""
#     You are a Grant Scout. Your job is to find active URLs for grants that match the user's brief.
#     1. Use the Tavily MCP to search for *official* funder pages.
#     2. Return a list of the top 3-5 most promising URLs.
#     3. Format your output as a JSON object with a 'discovered_leads' list.
#     4. Each lead must have 'url' and 'source'.
#     Do NOT visit the detailed links yet. Just find them.
#     """,
#     tools=[tavily_mcp],
#     output_key="discovered_leads",
#     output_schema=DiscoveredLeadsReport
# )

# # --- Step 2: Extractor ---
# extractor_agent = LlmAgent(
#     name="GrantExtractor",
#     model=Gemini(model=MODEL_NAME, retry_options=retry_config),
#     instruction="""
#     You are a Data Extractor. You will receive a list of {discovered_leads}.
    
#     LOOP through every URL found in the previous step:
#     1. Read the page content using Tavily.
#     2. Extract Budget, Deadline, Eligibility exactly as they appear.
#     3. If a field is missing, state "Not mentioned".
    
#     Return a final report containing all extracted data.
#     """,
#     tools=[tavily_mcp],
#     output_key="scout_final_report",
#     output_schema=ScoutReport
# )

# # --- Workflow ---
# root_agent = SequentialAgent(
#     name="tavily_assistant_agent",
#     description="Finds grants and extracts raw details.",
#     sub_agents=[finder_agent, extractor_agent]
# )

# # --- 5. EXECUTION BLOCK ---
# if __name__ == "__main__":
#     import asyncio
#     from google.adk.runners import Runner
#     from google.adk.sessions import InMemorySessionService
    
#     async def main():
#         print(f"🚀 Starting Grant Seeker Workflow...")
        
#         # 1. Initialize Session Service
#         session_service = InMemorySessionService()
        
#         # 2. Create the session explicitly
#         await session_service.create_session(
#             app_name="grant_seeker_test",
#             user_id="console_user",
#             session_id="test_session"
#         )
        
#         # 3. Initialize the runner
#         runner = Runner(
#             agent=root_agent,
#             app_name="grant_seeker_test",
#             session_service=session_service
#         )
        
#         # Define the input
#         query = "Find community garden grants for urban youth in Chicago"
#         user_msg = types.Content(role="user", parts=[types.Part(text=query)])

#         print(f"🔎 Searching for: {query}")
#         print("⏳ Agents are working... (This involves real searches)")
        
#         # Run and print results
#         final_text = ""
#         async for event in runner.run_async(
#             user_id="console_user",
#             session_id="test_session",
#             new_message=user_msg
#         ):
#             # Print final response if available
#             if event.is_final_response() and event.content and event.content.parts:
#                 final_text = event.content.parts[0].text

#         print("\n✅ Workflow Complete!")
#         print("--- Final Structured Output ---")
#         print(final_text)

#     # Run the async function
#     asyncio.run(main())
#     import asyncio
#     from google.adk.runners import Runner
#     from google.adk.sessions import InMemorySessionService
    
#     async def main():
#         print(f"🚀 Starting Grant Seeker Workflow...")
        
#         # 1. Initialize Session Service
#         session_service = InMemorySessionService()
        
#         # 2. CRITICAL FIX: Explicitly create the session first
#         await session_service.create_session(
#             app_name="grant_seeker_test",
#             user_id="console_user",
#             session_id="test_session"
#         )
        
#         # 3. Initialize the runner
#         runner = Runner(
#             agent=root_agent,
#             app_name="grant_seeker_test",
#             session_service=session_service
#         )
        
#         # Define the input
#         query = "Find community garden grants for urban youth in Chicago"
#         user_msg = types.Content(role="user", parts=[types.Part(text=query)])

#         print(f"🔎 Searching for: {query}")
#         print("⏳ Please wait (this involves searching and reading multiple pages)...")
        
#         # Run and print results
#         final_text = ""
#         async for event in runner.run_async(
#             user_id="console_user",
#             session_id="test_session",
#             new_message=user_msg
#         ):
#             # Print final response if available
#             if event.is_final_response() and event.content and event.content.parts:
#                 final_text = event.content.parts[0].text

#         print("\n✅ Workflow Complete!")
#         print("--- Final Structured Output ---")
#         print(final_text)

#     # Run the async function
#     asyncio.run(main())


import os
import dotenv
import asyncio
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams
from google.adk.models import Gemini
from google.genai import types
from pydantic import BaseModel, Field

# 1. Setup Environment
dotenv.load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# --- CHANGE #1: UPGRADE THE MODEL ---
# Use the more powerful Pro model, which is better at complex JSON generation.
MODEL_NAME = "gemini-pro-latest" 

# 2. Setup Tools
tavily_mcp = McpToolset(
    connection_params=StreamableHTTPServerParams(
        url="https://mcp.tavily.com/mcp/",
        headers={"Authorization": f"Bearer {TAVILY_API_KEY}"},
    ),
)

retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
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
# This agent's job is to produce a clean, structured list of leads for the next agent.
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

# --- Step 2: Extractor ---
extractor_agent = LlmAgent(
    name="GrantExtractor",
    model=Gemini(model=MODEL_NAME, retry_options=retry_config),
    instruction="""
    You are a Data Extractor. You will receive a list of {discovered_leads}.
    
    LOOP through every URL found in the previous step:
    1. Read the page content using Tavily.
    2. Extract Budget, Deadline, and Eligibility exactly as they appear.
    
    Return a final report containing all extracted data. 
    YOUR FINAL OUTPUT MUST BE ONLY A VALID JSON OBJECT with a 'found_grants' key.
    """,
    tools=[tavily_mcp],
    output_key="scout_final_report",
    # --- CHANGE #2: SIMPLIFY THE FINAL STEP ---
    # We remove the schema here and rely on the prompt to generate the JSON string.
    # This is more stable for the final agent in a SequentialAgent chain.
)

# --- Workflow ---
root_agent = SequentialAgent(
    name="tavily_assistant_agent",
    description="Finds grants and extracts raw details for the Analyst.",
    sub_agents=[finder_agent, extractor_agent]
)