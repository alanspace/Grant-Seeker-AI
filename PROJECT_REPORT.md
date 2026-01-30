# Grant Seeker AI - Project Report

## 1. Executive Summary
**Grant Seeker AI** is a sophisticated, multi-agent system designed to automate the grant-seeking lifecycle for non-profit organizations. Built as part of the Google ADK Capstone Project, it serves as an "Agent for Good" by streamlining three critical phases:
1.  **Discovery**: Finding relevant grants using detailed search strategies.
2.  **Compliance**: Analyzing complex guidelines to extract eligibility and requirements.
3.  **Drafting**: Generating tailored, compliant grant proposals.

The project is currently in a **functional prototype/MVP state**, featuring a complete end-to-end workflow from search to proposal generation.

## 2. Project Status
*   **Current State**: The application is operational ("Completed" status) with a working backend and frontend.
*   **Recent Activity**: Recent updates have focused on cost transparency and user control, specifically:
    *   **Search Thoroughness**: A new selector to control the depth of search (minimum results).
    *   **Token Tracking**: A display of estimated and actual token usage to manage API costs.
*   **Testing**: The project includes a suite of integration tests (`test_filters.py`, `test_advanced.py`) and debug scripts to ensure robustness.

## 3. Technical Architecture

The system utilizes a **Hybrid Multi-Agent Architecture** powered by the **Google Agent Development Kit (ADK)** and **Google Gemini 1.5 Flash**.

### Core Data Flow
1.  **User Input** (Streamlit): User defines mission, budget, and location.
2.  **Discovery Agent** (Backend):
    *   Uses **Tavily API** to search the web for opportunities.
    *   Implements "Smart Caching" (24h TTL) to prevent redundant queries.
3.  **Extraction Agent** (Backend):
    *   Runs in parallel (asyncio) to process multiple grant URLs simultaneously.
    *   Extracts 13 structured fields (Deadlines, Eligibility, etc.) into Pydantic models.
4.  **Writer Agent** (Backend):
    *   Uses **Gemini Flash** to draft a "Statement of Need" and "Alignment" section based on the extracted data and user context.

## 4. Technology Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Framework** | **Google ADK** | Core agent orchestration and lifecycle management. |
| **AI Model** | **Gemini 1.5 Flash** | Fast, cost-effective model for extraction and drafting. |
| **Frontend** | **Streamlit** | Interactive Python-based web UI (`home_page.py`). |
| **Search** | **Tavily API** | Specialized search tool for finding grant opportunities. |
| **Language** | **Python 3.10+** | Primary development language. |
| **Validation** | **Pydantic** | Ensures type safety for data exchange between agents. |
| **Data Source** | **Web + PDF** | Capable of scraping HTML and (planned/partial) PDF parsing. |

## 5. Repository Structure

The project is organized into clear backend and frontend logical units:

```text
/
├── backend/                  # Core Agent Logic
│   ├── adk_agent.py          # Main agent orchestrator
│   ├── writer_agent.py       # Specialist agent for proposal writing
│   ├── content_extractor.py  # Logic to parse texts/HTML
│   ├── tavily_client.py      # Search API wrapper
│   └── google_search_client.py
├── frontend/                 # Streamlit UI Components
│   ├── search_grants.py      # Search workflow UI
│   ├── grant_details.py      # detailed view of specific grants
│   ├── proposal_builder.py   # UI for the drafting phase
│   └── diagnostics.py        # System health/debug view
├── scripts/                  # Utility Scripts
│   ├── debug_tavily.py       # API connection tests
│   └── debug_google_cse.py
├── home_page.py              # Main Entry Point (Streamlit App)
├── test_*.py                 # Integration Tests (Filters, Advanced Logic)
├── ENHANCEMENT_PLAN.md       # Roadmap for future features
└── requirements.txt          # Python dependencies
```

## 6. Key Features Implementation

### A. The Writer Agent (`backend/writer_agent.py`)
This file defines a `LlmAgent` specifically prompted to act as a "Professional Grant Writer."
*   **Input**: Project details + Grant JSON (Eligibility, Budget, Deadline).
*   **Output**: A persuasive proposal draft emphasizing alignment with funder goals.
*   **Mechanism**: Uses `InMemorySessionService` to maintain context during the generation.

### B. Smart Caching
To optimize performance and cost, the system caches successful grant extractions in a hidden `.cache/` directory. This reduces response times for repeated queries from ~30s to ~7s.

### C. Search Thoroughness (New)
Users can now configure the "Minimum Results" they want. The system estimates the token cost (approx. 15k tokens per result) and displays it, giving users control over the trade-off between depth and cost.

## 7. Next Steps & Recommendations
Based on the `ENHANCEMENT_PLAN.md` and current state:
1.  **PDF Integration**: Complete the PDF-to-Image/Text pipeline to handle grant guidelines provided as PDF documents.
2.  **Iterative Search**: Refine the search loop to automatically broaden queries if the minimum result count isn't met.
3.  **Deployment**: The project is ready for Streamlit Cloud but could benefit from a Docker container for easier local setup.
