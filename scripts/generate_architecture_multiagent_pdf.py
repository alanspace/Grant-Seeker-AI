"""Generate a technical architecture + multi-agent details PDF for Grant Seeker AI."""

from datetime import date
from fpdf import FPDF


def sanitize_text(text: str) -> str:
    """Convert text to latin-1-safe content for FPDF output."""
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2026": "...",
        "\u00a0": " ",
        "\u2022": "-",
    }
    out = text or ""
    for src, dst in replacements.items():
        out = out.replace(src, dst)
    return out.encode("latin-1", "replace").decode("latin-1")


class ReportPDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Grant Seeker AI - Architecture & Multi-Agent Technical Summary", 0, 1, "C")
        self.set_font("Arial", "", 9)
        self.cell(0, 6, f"Generated: {date.today().isoformat()}", 0, 1, "C")
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", 0, 0, "C")

    def section(self, title: str):
        self.set_font("Arial", "B", 12)
        self.set_fill_color(236, 244, 255)
        self.cell(0, 8, sanitize_text(title), 0, 1, "L", True)
        self.ln(1)

    def body(self, text: str):
        self.set_font("Arial", "", 10)
        self.multi_cell(0, 5.5, sanitize_text(text))
        self.ln(1)

    def bullet(self, text: str):
        self.set_font("Arial", "", 10)
        self.multi_cell(0, 5.2, sanitize_text(f"- {text}"))


def build_report(output_path: str) -> None:
    pdf = ReportPDF()
    pdf.alias_nb_pages()
    pdf.add_page()

    pdf.section("1) System Architecture Summary")
    pdf.body(
        "Grant Seeker AI is implemented as a hybrid multi-agent architecture using Google ADK. "
        "The runtime combines sequential orchestration for planning/discovery and concurrent extraction "
        "for throughput. The primary orchestrator is GrantSeekerWorkflow in backend/adk_agent.py. "
        "User interactions come through Streamlit pages, then route into asynchronous ADK runs."
    )
    pdf.bullet("Frontend entry for discovery: frontend/search_grants.py -> execute_grant_workflow(...).")
    pdf.bullet("Backend orchestrator: backend/adk_agent.py -> GrantSeekerWorkflow.run(...).")
    pdf.bullet("Writer workflow: frontend/proposal_builder.py -> backend/writer_agent.py -> draft_proposal_section(...).")
    pdf.bullet("Per-agent sessions are managed with InMemorySessionService and unique session IDs.")

    pdf.section("2) End-to-End Runtime Pipeline")
    pdf.body("Pipeline implemented in GrantSeekerWorkflow.run(query):")
    pdf.bullet("Phase 0 - Query Generation Agent transforms user natural language into targeted Canadian search queries.")
    pdf.bullet("Phase 1 - Discovery search from Tavily/Google CSE returns candidates; Finder Agent selects top 5-7 leads.")
    pdf.bullet("Phase 2 - Parallel extraction invokes Extractor Agent across lead URLs with asyncio Semaphore(3).")
    pdf.bullet("Post-processing filters expired/USA/low-quality results, computes fit scores, validates viability, assigns IDs.")
    pdf.bullet("Optional Phase 3 - Writer Agent drafts proposal text from selected grant + user project narrative.")

    pdf.section("3) Multi-Agent Areas (Technical Inventory)")
    pdf.body("All technically verified multi-agent zones in the current codebase:")

    pdf.bullet(
        "A. Query Strategy Agent (backend/adk_agent.py:create_query_agent): "
        "ADK LlmAgent named QueryGenerator. Input: free-text mission/project description. "
        "Output: single optimized search query string with Canada-specific constraints."
    )
    pdf.bullet(
        "B. Discovery Ranking Agent (backend/adk_agent.py:create_finder_agent): "
        "ADK LlmAgent named GrantFinder. Input: JSON search results. Output schema: DiscoveredLeadsReport "
        "(list of DiscoveredLead entries). This is an agent-based filtering/ranking stage."
    )
    pdf.bullet(
        "C. Parallel Extraction Agent Pool (backend/adk_agent.py:create_extractor_agent + run): "
        "ADK LlmAgent named GrantExtractor with response schema GrantData. Multiple agent calls execute in "
        "parallel via asyncio.gather, bounded by MAX_CONCURRENT_EXTRACTIONS=3 using Semaphore."
    )
    pdf.bullet(
        "D. Iterative Multi-Attempt Orchestration (backend/adk_agent.py:run_with_minimum_results): "
        "A supervisory loop that repeatedly runs the full agent workflow with query variants until min_results "
        "or max attempts (5). This creates multi-round, multi-agent execution batches."
    )
    pdf.bullet(
        "E. Proposal Writer Agent (backend/writer_agent.py:writer_agent): "
        "Independent ADK LlmAgent named GrantWriter. Triggered from frontend/proposal_builder.py. "
        "Input: project narrative + selected grant fields; Output: markdown draft sections."
    )
    pdf.bullet(
        "F. Cross-agent typed contract layer: Pydantic schemas DiscoveredLeadsReport/DiscoveredLead/GrantData "
        "enforce strict, typed handoff between agent stages and UI."
    )

    pdf.section("4) Orchestration, Concurrency, and State")
    pdf.bullet("Runner orchestration uses google.adk.runners.Runner with run_async event streams per stage.")
    pdf.bullet("Session isolation: unique UUID-based session IDs created for query generation and each extraction.")
    pdf.bullet("Concurrency control: asyncio.Semaphore(MAX_CONCURRENT_EXTRACTIONS) prevents uncontrolled parallel calls.")
    pdf.bullet("Fan-out/fan-in pattern: list[lead] -> parallel extraction tasks -> flatten list[list[grant]] -> ranking/filtering.")
    pdf.bullet("Caching in orchestrator reduces repeated search/extraction calls (24h TTL, file-based JSON cache).")

    pdf.section("5) Multi-Agent Data Contracts")
    pdf.body("Core structured contracts used by agents:")
    pdf.bullet("DiscoveredLead: url, source, title.")
    pdf.bullet("DiscoveredLeadsReport: discovered_leads: list[DiscoveredLead].")
    pdf.bullet(
        "GrantData: title, funder, deadline, amount, description, detailed_overview, tags, eligibility, url, "
        "application_requirements, funding_nature, geography, fit_score, founder_demographics."
    )
    pdf.body(
        "Typed response schemas are configured in Gemini generation_config with response_mime_type='application/json' "
        "and response_schema set to Pydantic models."
    )

    pdf.section("6) Frontend Integration Points Using Multi-Agent Backend")
    pdf.bullet(
        "Search workflow (frontend/search_grants.py): execute_grant_workflow() calls workflow.run() or "
        "workflow.run_with_minimum_results() depending on min result target and active filters."
    )
    pdf.bullet(
        "Proposal builder (frontend/proposal_builder.py): generate_proposal_with_agent() imports writer_agent and "
        "calls draft_proposal_section(), which runs ADK writer agent through a dedicated Runner."
    )
    pdf.bullet(
        "Grant details export (frontend/grant_details.py): not an agent stage itself; consumes already extracted "
        "agent output and serializes to PDF."
    )

    pdf.section("7) Guardrails and Filtering Around Agent Output")
    pdf.bullet("Expired grant detection via deadline parsing and explicit 'expired' checks.")
    pdf.bullet("USA grant exclusion via geography/state-name screening for Canada-only scope.")
    pdf.bullet("Data viability filter rejects low-information outputs (prevents 'Untitled Grant' display).")
    pdf.bullet("Fit scoring ranks results and adaptive threshold keeps top relevance while preserving minimum count.")

    pdf.section("8) Reliability and Test Coverage Relevant to Multi-Agent")
    pdf.bullet("tests/test_iterative_search.py validates iterative multi-attempt behavior and minimum target logic.")
    pdf.bullet("tests/test_advanced.py validates robustness under ambiguous/specific/bilingual query scenarios.")
    pdf.bullet("tests/test_filters.py validates post-agent filtering relevance and data completeness rules.")

    pdf.section("9) Technical Notes and Observed Design Decisions")
    pdf.bullet("The architecture is hybrid, not a free-form autonomous swarm; stages are explicitly orchestrated.")
    pdf.bullet("Parallelism exists specifically in extractor stage; query/finder/writer are single-agent per invocation.")
    pdf.bullet("Iterative mode composes multiple full workflows, effectively multiplying agent invocations by attempt count.")
    pdf.bullet("Content extraction uses deterministic fallback strategies (Tavily/Google/PDF/HTML) before LLM extraction.")

    pdf.section("10) Concise Multi-Agent Map")
    pdf.body(
        "User Query -> QueryGenerator Agent -> Search Provider -> GrantFinder Agent -> Lead List -> "
        "[Parallel GrantExtractor Agent Calls xN (max 3 concurrent)] -> Filtering/Ranking -> UI Results -> "
        "(Optional) GrantWriter Agent for proposal drafting."
    )

    pdf.output(output_path)


if __name__ == "__main__":
    build_report("ARCHITECTURE_MULTI_AGENT_SUMMARY.pdf")
    print("Generated ARCHITECTURE_MULTI_AGENT_SUMMARY.pdf")