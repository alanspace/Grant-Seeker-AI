from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import AgentTool
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.planners import BuiltInPlanner
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams, StreamableHTTPServerParams
from mcp import StdioServerParameters
import os, dotenv
from google.genai import types
from google.adk.models import Gemini

dotenv.load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Setup Tavily MCP toolset
tavily_mcp = MCPToolset(
    connection_params=StreamableHTTPServerParams(
        url="https://mcp.tavily.com/mcp/",
        headers={
            "Authorization": f"Bearer {TAVILY_API_KEY}",
        },
    ),
)

retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1.0,
    http_status_codes=[429, 500, 503, 504],
)

# --- Discovery Agent ---
discovery_agent = LlmAgent(
    name="GrantDiscoveryAgent",
    model=Gemini(model="gemini-2.0-flash", retry_options=retry_config),
    instruction="""Search the web for grant opportunities matching the user query.
Return a list of URLs + title + 1-line relevance hint.
Prefer official funder sites + documents. when using the tavily search mcp, provide full country name instead of abbreviations.""",
    tools=[tavily_mcp],
    output_key="discovered_urls"
)

# --- Fit-Check Agent ---
fit_check_agent = LlmAgent(
    name="GrantFitAnalysisAgent",
    model=Gemini(model="gemini-2.0-flash", retry_options=retry_config),
    instruction="""Visit each URL from {discovered_urls} and fully crawl page + docs.Extract raw text + any budget, deadlines, eligibility as verbatim snippets only.Include attachments + provenance (where text came from). No guessing or decision-making — just collect evidence. Output structured raw extractions for every URL.""",
    tools=[tavily_mcp],
    output_key="fit_check_results"
)

# --- Structurer Agent ---
json_agent = LlmAgent(
    name="GrantStructurerAgent",
    model=Gemini(model="gemini-2.0-flash", retry_options=retry_config),
    instruction="""Take the fit-check results from {fit_check_results} and convert only "Highly relevant" or "Somewhat relevant" entries into a stable structured JSON with fields: grant_title, funder_name, url, deadline (YYYY-MM-DD or null), budget_cap ({amount, currency} or null), eligibility_summary, geographic_scope, match_rating, confidence_score, notes. Set missing/ambiguous fields to null and reflect uncertainty in confidence_score.""",
    tools=[tavily_mcp],
    output_key="structured_opportunities"
)

# --- Workflow (Sequential) Agent ---
root_agent = SequentialAgent(
    name="tavily_assistant_agent",
    sub_agents=[discovery_agent, fit_check_agent, json_agent]
)

# --- Root Agent (if needed) ---
# root_agent = LlmAgent(
#     name="tavily_assistant_agent",
#     model=Gemini(model="gemini-2.5-flash", retry_options=retry_config),
#     instruction="""You are the Grant Workflow Planner. Orchestrate the pipeline in this order: Discovery -> Fit-Check -> Structurer. Run each agent in sequence, outputs are automatically passed between them. Do not invent facts; rely on extracted evidence.

#     Brief tool descriptions (precise, actionable):
#     1. GrantDiscoveryAgent: Search the web and documents for grant opportunities that match the user's constraints (e.g., geography, budget cap, eligibility, deadlines). Return a JSON array of candidate items (url, title, short_justification).

#     2. GrantFitAnalysisAgent: For each candidate URL, fetch the page, extract verbatim evidence, evaluate four criteria (budget, location, eligibility, timeline), assign a rating ("Highly relevant" / "Somewhat relevant" / "Not relevant"), provide justification, criteria_details (with extracted_text), a confidence score, and notes if access was blocked or ambiguous.

#     3. GrantStructurerAgent: Take Fit-Check results and convert only "Highly relevant" or "Somewhat relevant" entries into a stable structured JSON with fields: grant_title, funder_name, url, deadline (YYYY-MM-DD or null), budget_cap ({amount, currency} or null), eligibility_summary, geographic_scope, match_rating, confidence_score, notes. Set missing/ambiguous fields to null and reflect uncertainty in confidence_score.
# """,
#     planner=BuiltInPlanner(
#         thinking_config=types.ThinkingConfig(
#             include_thoughts=True,
#             thinking_budget=1024,
#         )
#     ),
#     tools=[AgentTool(discovery_agent), AgentTool(fit_check_agent), AgentTool(json_agent)],
# )