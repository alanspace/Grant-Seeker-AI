# Grant Seeker AI

**An "Agents for Good" Multi-Agent System for the Google ADK Capstone Project**

![Project Status: In Progress](https://img.shields.io/badge/status-in--progress-yellow)

A sophisticated AI assistant that automates the grant-seeking lifecycle, empowering non-profits and researchers to secure funding more efficiently.

---

<!-- **ADD A GIF OF THE FINAL APP IN ACTION HERE. This is the most important visual element.** -->
<!-- To create a GIF, use a free tool like Giphy Capture or ScreenToGif to record your screen during the demo. -->

![Demo GIF](docs/demo.gif)

---

## Table of Contents

1. [The Pitch](#1-the-pitch)
2. [How It Works](#2-how-it-works)
3. [Technical Architecture](#3-technical-architecture)
4. [Technology Stack](#4-technology-stack)
5. [Setup and Run the Project](#5-setup-and-run-the-project)
6. [Our Team](#6-our-team)
7. [Future Work](#7-future-work)
8. [Acknowledgements](#8-acknowledgements)

---

## 1. The Pitch

### The Problem

_(Nakazzi to fill in: Define the target user (e.g., a grant writer at a small non-profit). Describe the pain points: countless hours spent searching, the complexity of decoding unique requirements for each grant, and the challenge of writing tailored proposals.)_

### Our Solution

_(Nakazzi to fill in: Describe our AI agent system as a collaborative team of specialist agents that automate the most burdensome tasks: discovery, analysis, and drafting. Frame it as an intelligent partner that empowers organizations to focus on their mission, not paperwork.)_

### The Value

_(Nakazzi to fill in: Quantify the benefits. Our solution saves hours per grant cycle, increases the quality of proposals, and democratizes access to funding for under-resourced organizations.)_

---

## 2. How It Works

Our application provides a four-step workflow powered by specialized AI agents:

1.  **Input Project Details** (Page 1): The user enters their organization details, project mission, focus area, budget range, and deadline into our Streamlit web interface.

2.  **Find & Extract Grants** (Backend Processing): When the user clicks "Find Grants," our intelligent agent workflow begins:

    - **GrantFinder Agent**: Searches the web using the Tavily API to discover relevant grant opportunities based on user criteria.
    - **GrantExtractor Agents**: Processes up to 5 promising grants in parallel (3 concurrent extractions) to extract structured data including 13 key fields (title, organization, amount, deadline, eligibility, description, focus area, contact, application URL, requirements, benefits, restrictions, and notes).
    - **Smart Caching**: Results are cached for 24 hours, reducing response time by 80% (from ~30s to ~7s) on repeated queries.

3.  **Review Results** (Page 2): Users see a structured list of discovered grants with all details displayed in an interactive card format.

4.  **Draft Proposal** (Page 3 - Optional): Users can select a specific grant and our **Writer Agent** generates a complete, tailored first draft of the grant proposal, ready for human review and refinement.

---

## 3. Technical Architecture

Our system is built using the **Google Agent Development Kit (ADK)** and implements a **Hybrid Multi-Agent Architecture** combining sequential and parallel processing:

**Phase 1 - Sequential Discovery:**

- **GrantFinder Agent**: Analyzes search results to identify 5-7 relevant grants
- Uses Tavily API for web search with intelligent query construction

**Phase 2 - Parallel Extraction:**

- **3 GrantExtractor Agents**: Run concurrently to extract detailed data from selected grants
- Controlled by asyncio Semaphore for optimal rate limit management
- Processes multiple grants simultaneously for speed

**Phase 3 - Proposal Generation (Separate Workflow):**

- **Writer Agent**: Generates tailored grant proposals on-demand
- Uses grant data + user context to create customized drafts

**Key Optimizations:**

- File-based caching system (24-hour TTL)
- Pydantic validation for data integrity
- Date-aware extraction with context injection
- Parallel processing with Semaphore(3) concurrency control

---

## 4. Technology Stack

- **Core Framework:** Google Agent Development Kit (ADK)
- **Language:** Python 3.10+
- **AI Model:** Google Gemini Flash (`gemini-flash-latest`)
- **Agent Tools:** Custom Tavily Python client with retry logic and error handling
- **Frontend:** Streamlit (multi-page application)
- **Data Validation:** Pydantic for type-safe models
- **Concurrency:** asyncio with Semaphore for parallel processing
- **Caching:** File-based cache system with MD5 hashing (24h TTL)
- **Testing:** pytest with 26 comprehensive unit tests
- **Deployment:** Ready for Streamlit Cloud or Google Cloud Run

---

## 5. Setup and Run the Project

### Prerequisites

- Python 3.10 or higher
- An API key for Google Gemini
- An API key and Custom Search Engine ID from Google Custom Search Engine

## 5. Setup and Run the Project

### Prerequisites

- Python 3.10 or higher
- pip or Conda for environment management
- An API key for Google Gemini (get from [Google AI Studio](https://aistudio.google.com/app/apikey))
- An API key for Tavily (get from [Tavily](https://tavily.com/))

### Installation Steps

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/alanspace/adk-grant-seeker-copilot.git
    cd adk-grant-seeker-copilot
    ```
2.  **Create and activate a virtual environment:**

    ```bash
    # Using venv
    python -m venv .venv
    .venv\Scripts\Activate.ps1  # Windows PowerShell
    # or
    source .venv/bin/activate  # Linux/Mac

    # Or using Conda
    conda create -n grantseeker-env python=3.10 -y
    conda activate grantseeker-env
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    pip install -r frontend/requirements-ui.txt
    ```
4.  **Set up your API keys:**
    - Create a file named `.env` in the root directory.
    - Add your API keys to this file:
    ```env
    GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
    TAVILY_API_KEY="YOUR_TAVILY_API_KEY"
    ```
5.  **Run the application:**
    ```bash
    streamlit run frontend/app.py
    ```
    The app will open in your browser at `http://localhost:8501`

### Running Tests

```bash
cd backend
pytest tests/ -v
```

---

## 6. Our Team

- **Shek Lun:** Technical Lead & AI Architect
- **Ante Krtalić:** Backend & DevOps Engineer
- **Mayank Kumar:** Frontend Developer
- **Nakazzi Kiyaga-Mulindwa:** Project & Presentation Lead

---

## 7. Future Work

While this prototype demonstrates our core vision, we have a clear roadmap for future development:

- **Expanded Grant Sources:** Integrate directly with major grant databases (Grants.gov, Foundation Directory) via their APIs
- **Budgeting Agent:** Introduce a new agent that helps users draft a budget justification section
- **Feedback & Revision Loop:** Allow users to provide feedback on generated proposals, enabling the Writer Agent to revise drafts iteratively
- **Advanced Caching:** Implement database-backed caching (Redis/PostgreSQL) for better persistence
- **User Accounts:** Add authentication and save search history per user
- **Export Options:** PDF/Word export for grant proposals
- **Production Deployment:** Deploy on Google Cloud Run or Streamlit Cloud with CI/CD pipeline

## 8. Acknowledgements

We would like to extend a special thank you to **Ujjwal Ruhal** for his valuable contributions during the initial UI conceptualization phase of this project.
