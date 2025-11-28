"""
Proposal Builder Page - Simple AI-assisted grant proposal generation
"""
import asyncio
import importlib
import math
import os
import sys

import streamlit as st
from st_copy import copy_button

# ----------------------------------------------------------------------
# Add backend to path for imports
# ----------------------------------------------------------------------
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "backend")
)

# ----------------------------------------------------------------------
# Page configuration
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Proposal Builder | Grant Seeker's Co-Pilot",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ----------------------------------------------------------------------
# Custom CSS
# ----------------------------------------------------------------------
st.markdown(
    """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display: none;}
        
        .builder-header {
            background-color: #eef6ff;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }
        
        .agent-response {
            background-color: #f0fff4;
            border-left: 4px solid #38a169;
            color: #2d3748;
            padding: 1rem 1.5rem;
            margin: 1rem 0;
            border-radius: 0 8px 8px 0;
            max-height: 580px;
            overflow-y: auto;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------
# Session‑state initialisation
# ----------------------------------------------------------------------
if "agent_draft" not in st.session_state:
    st.session_state.agent_draft = ""

# The **editable** draft – the only place the user edits text.
USER_DRAFT_KEY = "user_draft_text"
if USER_DRAFT_KEY not in st.session_state:
    st.session_state[USER_DRAFT_KEY] = ""

if "project_description" not in st.session_state:
    st.session_state.project_description = ""

# ----------------------------------------------------------------------
# Helper: call the writer agent
# ----------------------------------------------------------------------
def generate_proposal_with_agent(project_description: str, grant: dict) -> str:
    """
    Call the writer_agent to generate a proposal draft.

    Args:
        project_description: Description of the project
        grant: Grant details dictionary

    Returns:
        Generated proposal text from the AI agent
    """
    # Force re‑import to get a fresh module state (helps during dev)
    if "writer_agent" in sys.modules:
        del sys.modules["writer_agent"]

    writer_module = importlib.import_module("writer_agent")

    grant_json = {
        "source": grant.get("funder", "Unknown Funder"),
        "url": grant.get("url", ""),
        "eligibility": grant.get("eligibility", "Not specified"),
        "budget": grant.get("amount", "Not specified"),
        "deadline": grant.get("deadline", "Not specified"),
    }

    # writer_agent handles its own async loop internally
    result = writer_module.draft_proposal_section(
        project_description, grant_json
    )
    return result


# ----------------------------------------------------------------------
# Main UI
# ----------------------------------------------------------------------
def main():
    """Render the Proposal Builder page."""
    # ------------------------------------------------------------------
    # Grab the selected grant from session state (set on the Search page)
    # ------------------------------------------------------------------
    grant = st.session_state.get("selected_grant", None)
    if not grant:
        st.warning(
            "No grant selected. Please go back to the search page and choose a grant."
        )
        if st.button("🔙 Back to Search Grants"):
            st.switch_page("pages/1_🔍_Search_Grants.py")
        st.stop()

    # ------------------------------------------------------------------
    # Header
    # ------------------------------------------------------------------
    st.markdown(
        f"""
        <div class="builder-header" style="color: #2d3748;">
            <h2>✍️ Proposal Builder</h2>
            <p style="color: #4a5568;">
                Building proposal for: <strong>{grant.get('title', 'New Proposal')}</strong>
            </p>
            <p style="color: #718096; font-size: 0.9rem;">
                🏛️ {grant.get('funder', 'Unknown Funder')} |
                📅 Deadline: {grant.get('deadline', 'TBD')} |
                💰 {grant.get('amount', 'Amount TBD')}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ------------------------------------------------------------------
    # Project description input
    # ------------------------------------------------------------------
    st.markdown("### 📝 Describe Your Project")
    st.markdown(
        "*Provide details about your project so the AI can generate a tailored proposal*"
    )
    project_description = st.text_area(
        "Project Description",
        value=st.session_state.project_description,
        height=50,
        placeholder=(
            "Describe your project in detail. For example: A community garden "
            "project in downtown Chicago aiming to provide fresh produce to low‑income "
            "families and educational workshops for youth. We plan to transform 3 "
            "vacant lots into productive gardens serving 500+ residents..."
        ),
        label_visibility="collapsed",
    )
    # Keep the description in session state
    if project_description != st.session_state.project_description:
        st.session_state.project_description = project_description

    st.markdown("---")

    # ------------------------------------------------------------------
    # Two‑column layout: AI draft | Your editable draft
    # ------------------------------------------------------------------
    col_agent, col_user = st.columns(2)

    # --------------------------------------------------------------
    # LEFT COLUMN – AI Agent Draft
    # --------------------------------------------------------------
    with col_agent:
        st.markdown("### 🤖 AI Agent Draft")
        st.markdown("*Generated proposal from the AI agent*")

        # ----- Generate / Regenerate button -----
        if st.button(
            "✨ Generate Draft", type="primary", use_container_width=True
        ):
            if not st.session_state.project_description.strip():
                st.warning(
                    "Please describe your project above before generating a draft."
                )
            else:
                with st.spinner(
                    "AI Agent is generating your proposal draft... This may take a moment."
                ):
                    try:
                        draft = generate_proposal_with_agent(
                            st.session_state.project_description, grant
                        )
                        if draft:
                            st.session_state.agent_draft = draft
                            # Also pre‑fill the editable draft (optional but convenient)
                            st.session_state[USER_DRAFT_KEY] = draft
                            st.rerun()
                        else:
                            st.error(
                                "Failed to generate draft. Please try again."
                            )
                    except Exception as exc:  # pragma: no‑cover
                        st.error(f"Error generating draft: {exc}")

        # ----- Show the AI draft (if any) -----
        if st.session_state.agent_draft:
            st.markdown(
                f"""
                <div class="agent-response">
                    {st.session_state.agent_draft.replace(chr(10), "<br>")}
                </div>
                """,
                unsafe_allow_html=True,
            )
            # ----- Copy to user‑draft button -----
            if st.button(
                "📋 Copy to My Draft", use_container_width=True
            ):
                st.session_state[USER_DRAFT_KEY] = st.session_state.agent_draft
                st.success("Copied to your draft!")
        else:
            st.info(
                "Click 'Generate Draft' to get an AI‑generated proposal based on the grant requirements."
            )

    # --------------------------------------------------------------
    # RIGHT COLUMN – Editable Draft
    # --------------------------------------------------------------
    with col_user:
        st.markdown("### 📝 Your Draft")
        st.markdown("*Edit and finalize your proposal*")

        # ---- Placeholder / height logic (kept from original) ----
        _placeholder_text = (
            "Start writing your proposal here, or copy the AI‑generated draft and customize it..."
        )
        _chars_per_line = 70
        _line_height = 22
        _padding = 24
        _lines = sum(
            math.ceil(len(line) / _chars_per_line)
            for line in _placeholder_text.split("\n")
        )
        _min_height = max(40, int(_lines * _line_height + _padding))

        # If the draft is still empty we give it a modest height; once the user
        # starts typing we give the area plenty of room.
        height = (
            _min_height
            if not st.session_state[USER_DRAFT_KEY].strip()
            else 610
        )

        # ---- The editable text area ----
        st.text_area(
            "Your Proposal Draft",
            key=USER_DRAFT_KEY,          # <-- the crucial part
            height=height,
            placeholder=_placeholder_text,
            label_visibility="collapsed",
        )

        # ---- Download / Copy actions ----
        if st.session_state[USER_DRAFT_KEY].strip():
            st.download_button(
                label="Download",
                data=st.session_state[USER_DRAFT_KEY],
                file_name="draft.txt",
                mime="text/plain",
            )
            copy_button(st.session_state[USER_DRAFT_KEY])
        else:
            st.warning("Nothing to download yet.")
            st.warning("Nothing to copy yet.")

    # ------------------------------------------------------------------
    # Sidebar – quick tips
    # ------------------------------------------------------------------
    with st.sidebar:
        st.markdown("### 💡 Tips")
        st.markdown(
            """
            1. **Generate** an AI draft first  
            2. **Copy** it to your draft (or start from scratch)  
            3. **Customize** with your own details  
            4. **Save** / **download** the final version
            """
        )


if __name__ == "__main__":
    main()
