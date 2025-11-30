# import os
# import dotenv
# import asyncio
# from google.adk.agents import LlmAgent, SequentialAgent
# from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
# from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams
# from google.adk.models import Gemini
# from google.genai import types
# from pydantic import BaseModel, Field

# # 1. Setup Environment
# dotenv.load_dotenv()
# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# # 2. Configs
# # NOTE: Changed model to 'gemini-pro-latest' to match your API key capabilities
# MODEL_NAME = "gemini-pro-latest" 

# retry_config = types.HttpRetryOptions(
#     attempts=5,
#     exp_base=7,
#     initial_delay=1.0,
#     http_status_codes=[429, 500, 503, 504],
# )

# # 3. Setup Tools (Tavily MCP)
# tavily_mcp = MCPToolset(
#     connection_params=StreamableHTTPServerParams(
#         url="https://mcp.tavily.com/mcp/?tavilyApiKey=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",
#         headers={"Authorization": f"Bearer {TAVILY_API_KEY}"},
#     ),
# )

# # 4. Structured Output Schemas (The "Pro" Feature)
# class DiscoveredLead(BaseModel):
#     url: str = Field(description="Direct link to the grant page")
#     title: str = Field(description="Title of the grant or page")
#     relevance: str = Field(description="Why this is relevant (1 sentence)")

# class DiscoveredLeadsReport(BaseModel):
#     leads: list[DiscoveredLead]

# class GrantOpportunity(BaseModel):
#     grant_title: str | None
#     funder_name: str | None
#     url: str
#     deadline: str | None
#     budget_amount: str | None
#     eligibility_summary: str | None
#     match_rating: str = Field(description="'High', 'Medium', or 'Low'")
#     confidence_score: float

# class FinalReport(BaseModel):
#     opportunities: list[GrantOpportunity]

# # 5. Define Agents

# # --- Agent A: Discovery ---
# discovery_agent = LlmAgent(
#     name="GrantDiscovery",
#     model=Gemini(model=MODEL_NAME, retry_options=retry_config),
#     instruction="""
#     You are a Grant Scout. Search the web for grant opportunities matching the user query.
#     Return a list of the top 3-5 most promising URLs.
#     Use the Tavily MCP tool to search.
#     """,
#     tools=[tavily_mcp],
#     output_key="discovered_leads",
#     output_schema=DiscoveredLeadsReport # Force structured output
# )

# # --- Agent B: Extractor & Analyzer ---
# # Note: We combine extraction and structuring to save time/tokens in this sequential flow
# analysis_agent = LlmAgent(
#     name="GrantAnalyzer",
#     model=Gemini(model=MODEL_NAME, retry_options=retry_config),
#     instruction="""
#     You are a Grant Analyst. You will receive a list of {discovered_leads}.
    
#     For every URL in the list:
#     1. Read the page content using Tavily.
#     2. Extract: Title, Funder, Deadline, Budget, and Eligibility.
#     3. Rate the match based on the user's original intent.
    
#     Return a structured JSON report.
#     """,
#     tools=[tavily_mcp],
#     output_key="final_report",
#     output_schema=FinalReport # Force structured output
# )

# # --- Root: The Workflow ---
# root_agent = SequentialAgent(
#     name="GrantSeekerWorkflow",
#     description="Finds and analyzes grants.",
#     sub_agents=[discovery_agent, analysis_agent]
# )

# # --- CORRECTED EXECUTION BLOCK ---
# if __name__ == "__main__":
#     import asyncio
#     from google.adk.runners import Runner
#     from google.adk.sessions import InMemorySessionService
#     from google.genai import types 

#     async def main():
#         print(f"🚀 Starting Grant Seeker using {MODEL_NAME} and Tavily MCP...")
        
#         runner = Runner(
#             agent=root_agent,
#             app_name="grant_seeker_app",
#             session_service=InMemorySessionService()
#         )
        
#         query_text = "Find community garden grants for urban youth in Chicago"
        
#         # Wrap the input
#         user_msg = types.Content(role="user", parts=[types.Part(text=query_text)])

#         print("🤖 Agents are thinking... (This may take 10-20 seconds)")

#         # FIX: Use 'async for' with 'run_async' instead of 'await runner.run'
#         final_response_text = ""
        
#         async for event in runner.run_async(
#             user_id="console_user",
#             session_id="test_session",
#             new_message=user_msg
#         ):
#             # You can print intermediate steps if you want (optional)
#             # if event.content and "function_call" in str(event.content):
#             #     print(f"  -> Tool Call: {event.content}")

#             # Capture the final text
#             if event.is_final_response() and event.content and event.content.parts:
#                 final_response_text = event.content.parts[0].text
        
#         print("\n✅ Workflow Complete!")
#         print("--- Final Result ---")
#         print(final_response_text)
        
#     asyncio.run(main())
#     import asyncio
#     from google.adk.runners import Runner
#     from google.adk.sessions import InMemorySessionService
#     from google.genai import types  # Import types to wrap the text

#     async def main():
#         print(f"🚀 Starting Grant Seeker using {MODEL_NAME} and Tavily MCP...")
        
#         runner = Runner(
#             agent=root_agent,
#             app_name="grant_seeker_app",
#             session_service=InMemorySessionService()
#         )
        
#         query_text = "Find community garden grants for urban youth in Chicago"
        
#         # ADK requires the input to be wrapped in a Content object
#         user_msg = types.Content(role="user", parts=[types.Part(text=query_text)])

#         # Call .run() with the correct arguments
#         result = await runner.run(
#             user_id="console_user",
#             session_id="test_session",
#             new_message=user_msg
#         )
        
#         print("\n✅ Workflow Complete!")
#         print("--- Raw Text Output ---")
#         # The result is a response object, we access the text from the last turn
#         print(result.text)
        
#     asyncio.run(main())
#     from google.adk.runners import Runner
#     from google.adk.sessions import InMemorySessionService
    
#     async def main():
#         print(f"🚀 Starting Grant Seeker using {MODEL_NAME} and Tavily MCP...")
        
#         runner = Runner(
#             agent=root_agent,
#             app_name="grant_seeker_app", 
#             session_service=InMemorySessionService()
#         )
        
#         query = "Find community garden grants for urban youth in Chicago"
#         result = await runner.run(input=query)
        
#         print("\n✅ Workflow Complete!")
#         print("--- Raw Text Output ---")
#         print(result.text)
        
#         # Verify we got structured data
#         # Note: In a real app, we would access the structured object, but for CLI print text is fine
        
#     asyncio.run(main())


import os
import dotenv
import asyncio
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset  # Fixed capitalization
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams
from google.adk.models import Gemini
from google.genai import types
from pydantic import BaseModel, Field

# 1. Setup Environment
dotenv.load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# 2. Configs
# CRITICAL FIX: using the model we know works for your key
MODEL_NAME = "gemini-pro-latest" 

retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1.0,
    http_status_codes=[429, 500, 503, 504],
)

# 3. Setup Tools (Tavily MCP)
tavily_mcp = McpToolset(
    connection_params=StreamableHTTPServerParams(
        url="https://mcp.tavily.com/mcp/",
        headers={"Authorization": f"Bearer {TAVILY_API_KEY}"},
    ),
)

# 4. Structured Output Schemas
class DiscoveredLead(BaseModel):
    url: str = Field(description="Direct link to the grant page or document")
    title: str = Field(description="Title of the grant")
    snippet: str = Field(description="Why this is relevant")

class DiscoveredLeadsReport(BaseModel):
    opportunities: list[DiscoveredLead]

class StructuredGrant(BaseModel):
    grant_title: str | None
    funder_name: str | None
    url: str
    deadline: str | None
    budget_cap: str | None
    eligibility_summary: str | None
    match_rating: str = Field(description="'Highly relevant', 'Somewhat relevant', etc.")
    confidence_score: float
    notes: str | None

class FinalReport(BaseModel):
    structured_opportunities: list[StructuredGrant]

# 5. Define Agents

# --- Agent 1: Discovery ---
discovery_agent = LlmAgent(
    name="GrantDiscoveryAgent",
    model=Gemini(model=MODEL_NAME, retry_options=retry_config),
    instruction="""
    You are a Grant Scout. Search the web for grant opportunities matching the user query.
    Return a list of the top 5 most promising URLs.
    Use the Tavily MCP tool to search.
    Do NOT visit the detailed links yet. Just find them.
    """,
    tools=[tavily_mcp],
    output_key="discovered_urls",
    output_schema=DiscoveredLeadsReport
)

# --- Agent 2: Fit-Check & Structurer ---
# We combine these for efficiency in the Sequential flow
structurer_agent = LlmAgent(
    name="GrantStructurerAgent",
    model=Gemini(model=MODEL_NAME, retry_options=retry_config),
    instruction="""
    You are a Grant Analyst. You will receive a list of {discovered_urls}.
    
    For every URL in the list:
    1. Read the page content using Tavily.
    2. Extract: Title, Funder, Deadline, Budget, and Eligibility.
    3. Rate the match based on the user's original request.
    4. Output a JSON object for each grant.
    """,
    tools=[tavily_mcp],
    output_key="structured_opportunities",
    output_schema=FinalReport
)

# --- Root: The Workflow ---
root_agent = SequentialAgent(
    name="GrantSeekerWorkflow",
    description="Finds and analyzes grants.",
    sub_agents=[discovery_agent, structurer_agent]
)

# 6. Execution Block (For Testing)
if __name__ == "__main__":
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    
    async def main():
        print(f"🚀 Starting Grant Seeker using {MODEL_NAME} and Tavily MCP...")
        
        runner = Runner(
            agent=root_agent,
            app_name="grant_seeker_app",
            session_service=InMemorySessionService()
        )
        
        query_text = "Find community garden grants for urban youth in Chicago"
        user_msg = types.Content(role="user", parts=[types.Part(text=query_text)])

        print("🤖 Agents are working... (This will take 30-60 seconds)")
        
        final_text = ""
        async for event in runner.run_async(
            user_id="console_user",
            session_id="test_session",
            new_message=user_msg
        ):
            if event.is_final_response() and event.content and event.content.parts:
                final_text = event.content.parts[0].text
        
        print("\n✅ Workflow Complete!")
        print("--- Final JSON Result ---")
        print(final_text)
        
    asyncio.run(main())