"""
Proposal Builder Page - Simple AI-assisted grant proposal generation
"""
import asyncio
import importlib
import streamlit as st
from st_copy import copy_button
import sys
import os
import math

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Page configuration
st.set_page_config(
    page_title="Proposal Builder | Grant Seeker's Co-Pilot",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

USER_DRAFT_KEY = 'user_draft_text'
if USER_DRAFT_KEY not in st.session_state:
    USER_DRAFT_KEY = ''

# Custom CSS
st.markdown("""
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
        
        .draft-section {
            background-color: #f7fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 1.5rem;
            margin: 1rem 0;
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
        
        .user-draft {
            background-color: #ebf8ff;
            border-left: 4px solid #3182ce;
            padding: 1rem 1.5rem;
            margin: 1rem 0;
            border-radius: 0 8px 8px 0;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'agent_draft' not in st.session_state:
    st.session_state.agent_draft = ''

if 'user_draft' not in st.session_state:
    st.session_state.user_draft = ''

if 'project_description' not in st.session_state:
    st.session_state.project_description = ''

# Import the writer_agent module

def generate_proposal_with_agent(project_description: str, grant: dict) -> str:
    """
    Call the writer_agent to generate a proposal draft.
    
    Args:
        project_description: Description of the project
        grant: Grant details dictionary
    
    Returns:
        Generated proposal text from the AI agent
    """
    # Force reimport to get fresh module state
    if "writer_agent" in sys.modules:
        del sys.modules["writer_agent"]
    
    writer_module = importlib.import_module("writer_agent")
    
    # Map grant data to the format expected by writer_agent
    grant_json = {
        "source": grant.get("funder", "Unknown Funder"),
        "url": grant.get("url", ""),
        "eligibility": grant.get("eligibility", "Not specified"),
        "budget": grant.get("amount", "Not specified"),
        "deadline": grant.get("deadline", "Not specified"),
    }
    
    # Call the writer agent directly - it handles its own async loop
    result = writer_module.draft_proposal_section(project_description, grant_json)
    
    return result


def main():
    """Main function for the Proposal Builder page."""
    
    # Get selected grant from session state
    grant = st.session_state.get('selected_grant', None)
    if not grant:
        st.warning("No grant selected. Please go back to the search page and select a grant.")
        if st.button("🔙 Back to Search Grants"):
            st.switch_page("pages/1_🔍_Search_Grants.py")
        st.stop()
    
    # Header
    st.markdown(f"""
        <div class="builder-header" style="color: #2d3748;">
            <h2>✍️ Proposal Builder</h2>
            <p style="color: #4a5568;">Building proposal for: <strong>{grant.get('title', 'New Proposal')}</strong></p>
            <p style="color: #718096; font-size: 0.9rem;">🏛️ {grant.get('funder', 'Unknown Funder')} | 📅 Deadline: {grant.get('deadline', 'TBD')} | 💰 {grant.get('amount', 'Amount TBD')}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Project Description Input Section
    st.markdown("### 📝 Describe Your Project")
    st.markdown("*Provide details about your project so the AI can generate a tailored proposal*")
    
    project_description = st.text_area(
        "Project Description",
        value=st.session_state.project_description,
        height=50,
        placeholder="Describe your project in detail. For example: A community garden project in downtown Chicago aiming to provide fresh produce to low-income families and educational workshops for youth. We plan to transform 3 vacant lots into productive gardens serving 500+ residents...",
        label_visibility="collapsed"
    )
    
    # Update session state
    if project_description != st.session_state.project_description:
        st.session_state.project_description = project_description
    
    st.markdown("---")
    
    # Two-column layout: Agent Draft | Your Draft
    col_agent, col_user = st.columns(2)
    
    with col_agent:
        st.markdown("### 🤖 AI Agent Draft")
        st.markdown("*Generated proposal from the AI agent*")
        
        # Button to generate/regenerate agent draft
        if st.button("✨ Generate Draft", type="primary", use_container_width=True):
            if not st.session_state.project_description.strip():
                st.warning("Please describe your project above before generating a draft.")
            else:
                with st.spinner("AI Agent is generating your proposal draft... This may take a moment."):
                    try:
                        draft = generate_proposal_with_agent(
                            st.session_state.project_description,
                            grant
                        )
                        if draft:
                            st.session_state.agent_draft = draft
                            st.session_state[USER_DRAFT_KEY] = draft  # Auto-copy to user draft
                            st.rerun()
                        else:
                            st.error("Failed to generate draft. Please try again.")
                    except Exception as e:
                        st.error(f"Error generating draft: {str(e)}")
        
        # Display agent draft
        if st.session_state.agent_draft:
            st.markdown(f"""
                <div class="agent-response">
                    {(st.session_state.agent_draft.replace(chr(10), '<br>'))}
                </div>
            """, unsafe_allow_html=True)
            # Copy to user draft button
            if st.button("📋 Copy to My Draft", use_container_width=True):
                # st.rerun()
                st.session_state[USER_DRAFT_KEY] = st.session_state.agent_draft
                st.success("Copied to your draft!")
            
        else:
            st.info("Click 'Generate Draft' to get an AI-generated proposal based on the grant requirements.")
    with col_user:
        st.markdown("### 📝 Your Draft")
        st.markdown("*Edit and finalize your proposal*")
        
        # Editable text area for user's draft
        _placeholder_text = "Start writing your proposal here, or copy the AI-generated draft and customize it..."
        # Estimate height to fit placeholder: approximate chars per line, line height and padding
        _chars_per_line = 70
        _line_height = 22
        _padding = 24

        _lines = sum(math.ceil(len(line) / _chars_per_line) for line in _placeholder_text.split("\n"))
        _min_height = max(40, int(_lines * _line_height + _padding))

        _height = _min_height if not st.session_state[USER_DRAFT_KEY].strip() else 610

        user_draft = st.text_area(
            "Your Proposal Draft",
            key=USER_DRAFT_KEY,
            height=_height,
            placeholder=_placeholder_text,
            label_visibility="collapsed"
        )

        # if user_draft != st.session_state.user_draft:
        #     st.session_state.user_draft = user_draft
        
        # Update session state
        if user_draft != st.session_state.user_draft:
            st.session_state.user_draft = user_draft
        
        # Action buttons
        # btn_col1, btn_col2 = st.columns(2)
        
        # with btn_col1:
        #     if st.button("💾 Copy Draft", use_container_width=True):
        #         if st.session_state.user_draft:
        #             st.success("Draft copied!")
        #         else:
        #             st.warning("Nothing to save yet.")

        
        # with btn_col1:
        if st.session_state.user_draft:
            if st.download_button(
                label="Download",
                data=st.session_state[USER_DRAFT_KEY],
                file_name="draft.txt",
                mime="text/plain",
            ):
                st.success("File Downloaded!")
            copy_button(st.session_state.user_draft)
        else:
            st.warning("Nothing to download yet.")
            st.warning("Nothing to copy yet.")
        # with btn_col2:
        
        
    
    # Quick tips in sidebar
    with st.sidebar:
        st.markdown("### 💡 Tips")
        st.markdown("""
        1. **Generate** an AI draft first
        2. **Copy** it to your draft
        3. **Customize** with your details
        4. **Save** your final version
        """)


if __name__ == "__main__":
    main()
