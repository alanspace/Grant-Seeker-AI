# The Grant Seeker's Co-Pilot

**An "Agents for Good" Multi-Agent System for the Google ADK Capstone Project**

![Project Status: In Progress](https://img.shields.io/badge/status-in--progress-yellow)

A sophisticated AI assistant that automates the entire grant-seeking lifecycle, empowering non-profits and researchers to secure funding more efficiently.

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

---

## 1. The Pitch

### The Problem
*(Nakazzi to fill in: Clearly define the target user (e.g., a grant writer at a small environmental non-profit). Describe the pain points in detail: the countless hours spent searching databases, the complexity of decoding unique requirements for each grant, and the challenge of writing tailored, persuasive proposals under tight deadlines.)*

### Our Solution
*(Nakazzi to fill in: Describe our AI agent system as the solution. Explain that it's a collaborative team of specialist agents that automate the most burdensome tasks: discovery, analysis, and drafting. Frame it as an intelligent partner that empowers organizations to focus on their mission, not on paperwork.)*

### The Value
*(Nakazzi to fill in: Quantify the benefits. Our solution saves hundreds of hours per grant cycle, increases the quality and consistency of proposals, and ultimately democratizes access to funding for under-resourced but high-impact organizations.)*

---

## 2. How It Works

Our application provides a simple, three-step workflow for the user:

1.  **Input Project Details:** The user enters a description of their project, its goals, and its mission into a simple web form.
2.  **Discover & Analyze:** The **Scout Agent** searches the web for relevant grant opportunities. For each opportunity, the **Analyst Agent** reads the webpage or PDF to extract key information like deadlines, eligibility, and required proposal sections.
3.  **Draft Proposal:** The user selects a grant, and the **Writer Agent** uses the user's project details and the analyst's findings to generate a complete, tailored first draft of the grant proposal, ready for human review.

---

## 3. Technical Architecture

Our system is built on a collaborative multi-agent architecture managed by a central **Orchestrator**.

*(Nakazzi, with help from Hemanth & Shek Lun, to fill in: A brief description of how the Orchestrator delegates tasks to the Scout, Analyst, and Writer agents, and how data flows between them. The diagram is key here.)*

![Architecture Diagram](docs/architecture.png) <!-- The tech team will create this diagram using a tool like diagrams.net -->

---

## 4. Technology Stack

*   **Core Framework:** Google Agent Development Kit (ADK)
*   **Language:** Python 3.10+
*   **AI Model:** Google Gemini
*   **Frontend:** Streamlit
*   **Key Libraries:** Google Search API, BeautifulSoup4, PyMuPDF
*   **Deployment:** Docker, Google Cloud Run

---

## 5. Setup and Run the Project

### Prerequisites
*   Python 3.10 or higher
*   An API key for Google Gemini
*   An API key and Custom Search Engine ID from Google Custom Search Engine

### Installation Steps
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/YourUsername/adk-grant-seeker-copilot.git
    cd adk-grant-seeker-copilot
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    # On Windows, use: venv\Scripts\activate
    ```
3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Set up your API keys:**
    *   Create a file named `.env` in the root directory of the project.
    *   Add your API keys to this file in the following format:
    ```
    GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
    GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
    SEARCH_ENGINE_ID="YOUR_SEARCH_ENGINE_ID"
    ```
5.  **Run the application:**
    ```bash
    streamlit run app.py
    ```
---

## 6. Our Team

*   **Shek Lun:** Technical Lead & Backend Owner
*   **Hemanth Reganti:** Chief Architect & Strategic Advisor
*   **Gopika Devi:** Frontend & UI Developer
*   **Nakazzi Kiyaga-Mulindwa:** Project & Presentation Lead

---

## 7. Future Work

While this prototype demonstrates our core vision, we have a clear roadmap for future development:

*   **Expanded Grant Sources:** Integrate directly with major grant databases like GrantStation and Foundation Directory Online via their APIs.
*   **Budgeting Agent:** Introduce a new agent that helps users draft a budget justification section based on their project details.
*   **Feedback & Revision Loop:** Allow users to provide feedback on the generated text, which the Writer Agent can use to revise and improve the draft.
*   **Analytics Dashboard:** Provide users with insights into the types of grants they are most often matched with and their application success rates.
