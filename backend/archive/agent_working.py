from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import AgentTool
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.planners import BuiltInPlanner
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams, StreamableHTTPServerParams
from mcp import StdioServerParameters
import os, dotenv
from google.genai import types
from google.adk.models import Gemini
from pydantic import BaseModel

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

# Retry configuration for Gemini model calls
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1.0,
    http_status_codes=[429, 500, 503, 504],
)

# Structured output
# ----- Pydantic Model for Discovery Agent -----
class GrantDiscovery(BaseModel):
    grant_title: str | None
    funder_name: str | None
    url: str
    deadline_parsed: str | None
    budget_raw: list[str]
    budget_parsed: dict | None
    geographic_raw: list[str]
    contacts_raw: list
    attachments: list

# ----- Pydantic Model for Fit-Check Agent -----
class GrantFitCheckResult(BaseModel):
    url: str
    title: str | None
    rating: str
    justification: str
    criteria_details: dict
    confidence: float
    notes: str | None
    


# ------------------ Agents ------------------
# --- Discovery Agent ---
discovery_agent = LlmAgent(
    name="GrantDiscoveryAgent",
    model=Gemini(model="gemini-2.0-flash", retry_options=retry_config),
    instruction="""You are the Grant Discovery Agent. Your sole job is to locate candidate grant pages or documents that may be relevant to the user's brief. Do not evaluate whether a candidate is a good fit - you only collect leads.

Steps:

Translate the user brief into search queries and run web searches (Google Search or Tavily MCP). Include official funder sites, grant databases, PDFs, and credible aggregators.

For each candidate you find, return a minimal object with:

url (string) - direct URL or local file path. If a local upload exists, include /mnt/data/agent.py as a url item.

title (string | null) - page/document title if available

snippet (string | null) - 1-2 sentence justification: why this link is a candidate (mention one matching element, e.g., "mentions water projects", "awards up to $150,000")

source_type (string) - one of: "funder_site", "pdf", "database", "blog", "other"

crawl_hint (string | null) - short note for the next agent (e.g., "contains PDFs", "many attachments", "requires javascript")

Limit results to a reasonable number (e.g., top 10). Prefer authoritative sources over blog posts.

Output JSON named opportunities:

{ "opportunities": [ { "url":"...", "title":"...", "snippet":"...", "source_type":"funder_site", "crawl_hint":null }, ... ] }


Rules:

Do not extract detailed fields (budget, deadline, eligibility) here - the crawler does that.

If no candidates found, return { "opportunities": [] , "note":"reason" }.""",
    tools=[tavily_mcp],
    output_key="discovered_urls"
)

# --- Fit-Check Agent ---
fit_check_agent = LlmAgent(
    name="GrantFitAnalysisAgent",
    model=Gemini(model="gemini-2.0-flash", retry_options=retry_config),
    instruction="""You are the Grant Fit Analysis Agent.

Input Provided:

A list of URLs stored in {discovered_urls} that the Discovery Agent found.

Your Task:

For each URL in {discovered_urls}, visit the site/document and crawl the full page — read every word, inspect all relevant sections (PDFs, attachments).

From the content you extract, determine if the grant opportunity fits these four criteria:
- Budget: Is the award amount or budget cap aligned with the user's requirement?
- Location / Geographic Scope: Is the opportunity within the required region (e.g., US/Canada)?
- Eligibility: Are small nonprofits (or the specific applicant type) eligible and is the project focus aligned (e.g., community-led water access)?
- Timeline / Deadline: Does the opportunity have a deadline within the user's specified window?

For each grant, output:
 - url — the URL you evaluated.
 - title — the opportunity title (if found).
 - rating — one of: “Highly relevant”, “Somewhat relevant”, “Not relevant”.
 - justification — 2-3 sentences referencing exact quotes that led to your rating.
 - criteria_details — an object with each criterion (budget, location, eligibility, timeline) mapped to:
 • meets: true/false/unknown
 • extracted_text: the verbatim quote you used.
 - confidence — a number between 0.0 and 1.0 reflecting your confidence in the fit.

notes — any extra caveats (e.g., “Budget cap found but in CAD, convert needed”, “Deadline not clearly stated”).

Output format should be:

{
  "results": [
    {
      "url": "...",
      "title": "...",
      "rating": "...",
      "justification": "...",
      "criteria_details": {
        "budget": { "meets": true, "extracted_text": "..." },
        "location": { "meets": true, "extracted_text": "..." },
        "eligibility": { "meets": false, "extracted_text": "..." },
        "timeline": { "meets": unknown, "extracted_text": "..." }
      },
      "confidence": 0.60,
      "notes": "..."
    },
    … 
  ]
}


Important:

CALL THE MCP TOOLS ATLEAST 3 TIMES AS TO FULLY CRAWL EACH PAGE/DOCUMENT. YOU MUST NOT WORRY ABOUT RATE LIMITS OR COSTS — THE MCP HANDLES THAT.

Do not skip crawling full content — you must inspect all sections of the link/document.

If any field cannot be confirmed with a direct quote, mark it as meets=false or unknown (if ambiguous) and reduce confidence.

No assumptions or hallucinations — always base your output on extracted text.

Only once you finish this step, the results will be passed to the next agent.

Thank you — your thorough evaluation ensures only good matches move forward.""",
    tools=[tavily_mcp],
    output_key="fit_check_results"
)

# --- Structurer Agent ---
json_agent = LlmAgent(
    name="GrantStructurerAgent",
    model=Gemini(model="gemini-2.0-flash", retry_options=retry_config),
    instruction="""You are the Grant Structurer Agent. You receive raw page_extractions from the Page Crawler. Your job is to normalize and package extracted evidence into a consistent data envelope for the Analyst. You do not assess eligibility or decide relevance - only normalize and mark ambiguities.

Steps:

For each page_extraction object:

Extract a canonical grant_record with the following fields, filling with best-effort parsed values but do not infer or set a pass/fail flag:

grant_title (string|null) - prefer page title, fallback to first H1 or first sentence.

funder_name (string|null) - any explicit funder/org name found.

url (string)

deadline_raw (array of strings) - copy deadline_candidates (verbatim).

budget_raw (array of strings) - copy budget_candidates (verbatim).

eligibility_raw (array of strings)

geographic_raw (array of strings)

contacts_raw (array)

attachments - pass through the attachments list

full_text_excerpt - best 200-500 chars showing funder priorities (verbatim)

confidence_notes - string explaining which fields are ambiguous or missing (e.g., "no explicit deadline; budgets are ranges; currency CAD")

Attempt light normalization only:

For explicit dates like "Oct 15, 2025" produce deadline_parsed (YYYY-MM-DD) if unambiguous, otherwise leave deadline_parsed = null and add a note.

For explicit amounts like "$150,000" produce budget_parsed as { amount:150000, currency:"CAD" } only if currency is explicit; otherwise budget_parsed=null.

Output JSON named structured_opportunities:

{ "structured_opportunities":[ { "grant_title":"...", "funder_name":"...", "url":"...", "deadline_raw":[...], "deadline_parsed": "YYYY-MM-DD" | null, "budget_raw":[...], "budget_parsed":{...}|null, "eligibility_raw":[...], "geographic_raw":[...], "contacts_raw":[...], "attachments":[...], "full_text_excerpt":"...", "confidence_notes":"..." }, ... ] }


Rules:

Never mark meets or rating here. Those are the Analyst agent's responsibility.

If parsing/normalization is uncertain, prefer leaving *_parsed fields null and explain why in confidence_notes.

Preserve all provenance pointers from the crawler so the Analyst can re-verify.""",
    tools=[tavily_mcp],
    output_key="structured_opportunities"
)

# --- Workflow (Sequential) Agent ---
# root_agent = SequentialAgent(
#     name="tavily_assistant_agent",
#     sub_agents=[discovery_agent, fit_check_agent, json_agent]
# )

# --- Root Agent (if needed) ---
root_agent = LlmAgent(
    name="tavily_assistant_agent",
    model=Gemini(model="gemini-2.5-flash", retry_options=retry_config),
    instruction="""You are the Grant Workflow Planner. Orchestrate the pipeline in this order: Discovery -> Fit-Check -> Structurer. Run each agent in sequence, outputs are automatically passed between them. Do not invent facts; rely on extracted evidence.

    Brief tool descriptions (precise, actionable):
    1. GrantDiscoveryAgent: Search the web and documents for grant opportunities that match the user's constraints (e.g., geography, budget cap, eligibility, deadlines). Return a JSON array of candidate items (url, title, short_justification).

    2. GrantFitAnalysisAgent: For each candidate URL, fetch the page, extract verbatim evidence, evaluate four criteria (budget, location, eligibility, timeline), assign a rating ("Highly relevant" / "Somewhat relevant" / "Not relevant"), provide justification, criteria_details (with extracted_text), a confidence score, and notes if access was blocked or ambiguous.

    3. GrantStructurerAgent: Take Fit-Check results and convert only "Highly relevant" or "Somewhat relevant" entries into a stable structured JSON with fields: grant_title, funder_name, url, deadline (YYYY-MM-DD or null), budget_cap ({amount, currency} or null), eligibility_summary, geographic_scope, match_rating, confidence_score, notes. Set missing/ambiguous fields to null and reflect uncertainty in confidence_score.
""",
    planner=BuiltInPlanner(
        thinking_config=types.ThinkingConfig(
            include_thoughts=True,
            thinking_budget=1024,
        )
    ),
    sub_agents=[discovery_agent, fit_check_agent, json_agent],
    tools=[tavily_mcp],
)