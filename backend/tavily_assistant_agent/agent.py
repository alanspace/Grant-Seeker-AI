import os
import dotenv
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams
from google.adk.models import Gemini
from google.genai import types
from pydantic import BaseModel, Field

dotenv.load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# 1. Setup Tools
tavily_mcp = MCPToolset(
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

# 2. Refined Pydantic Schemas (Non-Judgmental)
# The Scout only captures FACTS, not RATINGS.

class DiscoveredLead(BaseModel):
    url: str = Field(description="Direct link to the grant page or document")
    source: str = Field(description="Name of the organization or website")

class DiscoveredLeadsReport(BaseModel):
    discovered_leads: list[DiscoveredLead]

class RawGrantData(BaseModel):
    url: str
    funder_name: str | None
    grant_title: str | None
    # We use '_text' to imply raw extraction, not parsed values
    budget_text: str | None = Field(description="Verbatim budget mentions, e.g., 'Up to $50k'")
    deadline_text: str | None = Field(description="Verbatim deadline mentions, e.g., 'Oct 15th'")
    eligibility_text: str | None = Field(description="Raw text describing who can apply")
    description_summary: str = Field(description="A neutral 2-sentence summary of what this grant funds")
    
class ScoutReport(BaseModel):
    # This is the final output of the Scout Agent
    found_grants: list[dict]

# 3. Agents

# --- Step 1: Finder (The Hunter) ---
# Goal: Find lists of URLs. Do not read them deep yet.
finder_agent = LlmAgent(
    name="GrantFinder",
    model=Gemini(model="gemini-2.0-flash", retry_options=retry_config),
    instruction="""
    You are a Grant Scout. Your job is to find active URLs for grants that match the user's brief.
    
    1. Analyze the user's request.
    2. Use the Tavily MCP to search for *official* funder pages, RFPs, or reliable databases.
    3. Look for "Apply" pages, Guidelines PDFs, or Program details.
    4. Return a list of the top 5-7 most promising URLs.
    5. When searching for country specific grants, use the full country name instead of abbreviations like CA, US etc.
    
    Do NOT visit the detailed links yet. Just find them.
    """,
    tools=[tavily_mcp],
    output_key="discovered_leads",
    output_schema=DiscoveredLeadsReport # Enforce a clean list of URLs
)

# --- Step 2: Extractor (The Gatherer) ---
# Goal: Visit each URL and scrape the data. Do not judge relevance.
extractor_agent = LlmAgent(
    name="GrantExtractor",
    model=Gemini(model="gemini-2.0-flash", retry_options=retry_config),
    instruction="""
    You are a Data Extractor. You will receive a list of {discovered_leads}.
    
    Your goal is to visit every URL in that list and extract raw data.
    
    LOOP through every URL found in the previous step:
    1. Read the page content using Tavily (or similar tool).
    2. Extract the specific fields (Budget, Deadline, Eligibility) exactly as they appear in the text.
    3. If a field is missing, explicitly state "Not mentioned".
    4. Do NOT rate the grant (e.g., do not say "Highly Relevant"). Just report facts.
    
    Return a final report containing all extracted data.
    """,
    tools=[tavily_mcp],
    output_key="scout_final_report",
    output_schema=ScoutReport # This forces the final output to be your structured JSON
)

# --- Workflow ---
# Use SequentialAgent. It is deterministic: Find -> Extract.
root_agent = SequentialAgent(
    name="tavily_assistant_agent",
    description="Finds grants and extracts raw details for the Analyst.",
    sub_agents=[finder_agent, extractor_agent]
)