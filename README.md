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

The Grant Seeker AI is a sophisticated, collaborative multi-agent AI system designed to serve as an intelligent partner for non-profit organizations, transforming the grant-seeking process from a fragmented, weeks-long ordeal into a streamlined, automated workflow.

For small to medium, high-impact non-profits, the mission is vital, but the administrative burden of grant seeking is crippling. Dedicated grant writers and staff face immense pain points that divert critical resources away from doing good, hindering organizations from accessing the capital they need to survive and thrive. Current workflows are manual, fragmented, and inefficient.
The key challenges addressed by this project include:
Endless Discovery: Countless hours are lost manually scanning databases and the web for relevant opportunities, lacking a tireless researcher constantly monitoring the landscape.
Compliance Complexity: Decoding complex guidelines from various websites and PDFs to extract essential information—such as key requirements, deadlines, and eligibility criteria—is highly error-prone and tedious.
The Drafting Challenge: Writing high-quality, tailored proposals that strictly adhere to specific funder requirements is difficult to achieve at scale, especially when managing tight deadlines.

### Our Solution

The Grant Seeker AI is built as a true Agent for Good, automating the most burdensome tasks: discovery, analysis, and drafting. This approach provides an intelligent partner that empowers organizations to focus on their mission, not paperwork.
#### Core Concept and Architecture
The project’s innovation lies in a specialized team of AI agents coordinated by an intelligent Orchestrator. Instead of a simple chatbot, we have built a pipeline of distinct agents that collaborate to automate the workflow from start to finish, delivering a streamlined one-button flow.

#### The Specialized Agents
* The Finder Agent - Discovery 
This agent acts as a tireless researcher, scanning the web to find grant opportunities that match the user’s specific project mission and funding needs.
* The Create Extractor Agent and Create Query Agent - Compliance
These  agents function as  compliance officers, reading through dense guidelines and PDFs to extract and analytically structure actionable intelligence, creating a proposal requirements blueprint.
* The Writer Agent - Drafting
This agent acts as a professional grant writer, combining the user's narrative with the Analyst’s strict blueprint to generate a compliant, persuasive, and well-formatted proposal.
#### ESG Context
Our project’s central idea of an Agent for Good is pertinent as it is intrinsically related to the Environmental, Social and Corporate Governance (ESG) framework, specifically the Governance pillar, and the crucial issue of Business Resilience and Corporate Governance. Utilizing the Grant Seeker AI to embrace transparency plays an important role in sustainability reporting, allowing non-profit organizations to monitor impact, automate reporting, and engage donors more effectively.

#### Project Journey
Bringing this vision to life required agility and collaboration. This application was created by The Orchestrators, a team of three developers and a project manager. Despite being geographically dispersed, the team leveraged diverse perspectives and worked across time zones to integrate these agents into a seamless Streamlit interface. This collaboration was crucial in designing a tool that is not just technically sound, but empathetic to the needs of the global non-profit community.


### The Value

The Grant Seeker AI serves as a force multiplier, giving smaller organizations the professional capacity of a large fundraising department.
The quantifiable benefits include:
* Time Savings: We automate the entire workflow, potentially saving hundreds of hours per grant cycle.
* Quality and Consistency: By strictly adhering to the "Proposal Requirements" blueprint provided by the Analyst Agent, our system maximizes success rates through compliance.
* Democratization: Ultimately, this project achieves the Agents for Good mission by removing resource hurdles, thereby democratizing access to funding for under-resourced organizations. This allows non-profits to focus on their core mission rather than paperwork.

#### Citations

Anastasiia Skok. ESG for NGOs: How Sustainable Development Unlocks New Funding and Partnership Opportunities. https://www.bdo.ua/en-gb/insights-1/information-materials/2025/esg-for-ngos-how-sustainable-development-unlocks-new-funding-and-partnership-opportunities, 2025. BDO.

AnhNguyen. EU’s CSRD Set to Reshape Corporate-Nonprofit Partnerships by 2025.  https://senecaesg.com/insights/eus-csrd-set-to-reshape-corporate-nonprofit-partnerships-by-2025/#:~:text=The%20CSRD's%20emphasis%20on%20sustainability,Sources:. 2025. Seneca Technologies Pte. Ltd

Barbara Bijelic, Benjamin Michel, and Konstantin Mann. Behind ESG Ratings.  https://www.oecd.org/content/dam/oecd/en/publications/reports/2025/02/behind-esg-ratings_4591b8bb/3f055f0c-en.pdf, 2025. © OECD 2025.  This is an adaptation of an original work by the OECD. The opinions expressed and arguments employed in this adaptation should not be reported as representing the official views of the OECD or of its Member countries. 

Directorate-General for Internal Market, Industry, Entrepreneurship and SMEs.  Corporate sustainability and responsibility. https://single-market-economy.ec.europa.eu/industry/sustainability/corporate-sustainability-and-responsibility_en#esg-environmental-social-and-corporate-governance, 2025.  European Commission.

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
