# Grant Co-Pilot

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
*(Nakazzi to fill in: Define the target user (e.g., a grant writer at a small non-profit). Describe the pain points: countless hours spent searching, the complexity of decoding unique requirements for each grant, and the challenge of writing tailored proposals.)*

### Our Solution
*(Nakazzi to fill in: Describe our AI agent system as a collaborative team of specialist agents that automate the most burdensome tasks: discovery, analysis, and drafting. Frame it as an intelligent partner that empowers organizations to focus on their mission, not paperwork.)*

### The Value
*(Nakazzi to fill in: Quantify the benefits. Our solution saves hours per grant cycle, increases the quality of proposals, and democratizes access to funding for under-resourced organizations.)*

---

## 2. How It Works

Our application provides a simple, three-step workflow for the user:

1.  **Input Project Details:** The user enters a description of their project into our web interface.
2.  **Discover & Analyze:** The user clicks "Find Grants." In the background, our **Sequential Agent Workflow** begins:
    *   The **Discovery Agent** uses the Tavily API to find relevant grant opportunities on the web.
    *   The **Analysis Agent** then takes that list of URLs, revisits them with Tavily to read the full content, and extracts key details like budget, deadline, and eligibility into a structured JSON format.
3.  **Draft Proposal:** The user selects a grant from the structured list. Our **Writer Agent** then takes the user's project details and the analyzed grant data to generate a complete, tailored first draft of the grant proposal, ready for human review.

---

## 3. Technical Architecture

Our system is built using the **Google Agent Development Kit (ADK)** and follows a **Sequential Multi-Agent** pattern. This ensures a reliable, deterministic workflow where each specialized agent performs its task in a specific order.

*(Nakazzi, with help from Shek Lun & Ante, to fill in: A brief description of the sequential flow: Discovery -> Analysis. The diagram is key here.)*

![Architecture Diagram](docs/architecture.png) <!-- The tech team will create this diagram using a tool like diagrams.net -->

---

## 4. Technology Stack

*   **Core Framework:** Google Agent Development Kit (ADK)
*   **Language:** Python 3.11+
*   **AI Model:** Google Gemini (`gemini-pro-latest`)
*   **Agent Tools:** Tavily (via Remote MCP) for web search and scraping.
*   **Frontend:** Streamlit
*   **Deployment:** Docker, Google Cloud Run

---

## 5. Setup and Run the Project

### Prerequisites
*   Python 3.10 or higher
*   An API key for Google Gemini
*   An API key and Custom Search Engine ID from Google Custom Search Engine

## 5. Setup and Run the Project

### Prerequisites
*   Conda for environment management.
*   An API key for Google Gemini.
*   An API key for Tavily.

### Installation Steps
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/[YourUsername]/adk-grant-seeker-copilot.git
    cd adk-grant-seeker-copilot
    ```
2.  **Create and activate the Conda environment:**
    ```bash
    conda create -n grantseeker-env python=3.11 -y
    conda activate grantseeker-env
    ```
3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Set up your API keys:**
    *   Create a file named `.env` in the root directory.
    *   Add your API keys to this file:
    ```
    GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
    TAVILY_API_KEY="YOUR_TAVILY_API_KEY"
    ```
5.  **Run the application:**
    ```bash
    streamlit run app.py
    ```
---

## 6. Our Team

*   **Shek Lun:** Technical Lead & AI Architect
*   **Ante Krtalić:** Backend & DevOps Engineer
*   **Mayank Kumar:** Frontend Developer
*   **Nakazzi Kiyaga-Mulindwa:** Project & Presentation Lead

---

## 7. Future Work

While this prototype demonstrates our core vision, we have a clear roadmap for future development:

*   **Expanded Grant Sources:** Integrate directly with major grant databases via their APIs.
*   **Budgeting Agent:** Introduce a new agent that helps users draft a budget justification section.
*   **Feedback & Revision Loop:** Allow users to provide feedback on the generated text, which the Writer Agent can use to revise the draft.

## 8. Acknowledgements

We would like to extend a special thank you to **Ujjwal Ruhal** for his valuable contributions during the initial UI conceptualization phase of this project.