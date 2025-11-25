"""
Proposal Builder Page - Simple AI-assisted grant proposal generation
"""
import streamlit as st
from st_copy import copy_button
import sys
import os

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Page configuration
st.set_page_config(
    page_title="Proposal Builder | Grant Seeker's Co-Pilot",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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

# =============================================================================
# API INTEGRATION (Commented - uncomment when API is available)
# =============================================================================
# import requests
# 
# API_BASE_URL = "https://your-api-endpoint.com/api/v1"
# 
# def get_agent_draft(grant_id: str, project_details: dict) -> str:
#     """
#     Fetch AI-generated proposal draft from the agent.
#     
#     Args:
#         grant_id: ID of the selected grant
#         project_details: Dictionary with project information
#     
#     Returns:
#         Generated proposal draft text from the agent
#     """
#     try:
#         payload = {
#             "grant_id": grant_id,
#             "project_details": project_details
#         }
#         response = requests.post(f"{API_BASE_URL}/proposals/generate", json=payload, timeout=60)
#         response.raise_for_status()
#         
#         data = response.json()
#         return data.get("draft", "")
#     
#     except requests.RequestException as e:
#         st.error(f"Failed to generate draft: {str(e)}")
#         return None
# =============================================================================

# Sample agent-generated draft (mock data for demonstration)
SAMPLE_AGENT_DRAFT = """# Grant Proposal: Community Garden Initiative

## Executive Summary

The Urban Green Initiative respectfully requests $35,000 from the Green Earth Foundation to support the expansion of our Community Garden Network program. This comprehensive initiative will transform three vacant lots in Chicago's South Side into productive community gardens, serving over 500 residents and providing fresh produce to families experiencing food insecurity.

## Statement of Need

Chicago's South Side faces significant challenges in food access and nutrition. According to the USDA, this area qualifies as a food desert, with residents traveling an average of 4.2 miles to reach the nearest full-service grocery store. Nearly 28% of households experience food insecurity, compared to the national average of 10.5%.

## Goals & Objectives

**Goal 1: Expand Community Garden Infrastructure**
- Objective 1.1: By June 2025, secure land use agreements for three vacant lots
- Objective 1.2: By August 2025, complete installation of raised beds, irrigation systems, and tool storage
- Objective 1.3: By September 2025, have all 150 garden plots allocated to community members

**Goal 2: Build Community Capacity**
- Objective 2.1: By July 2025, recruit and train 50 community garden leaders
- Objective 2.2: By December 2025, conduct 24 educational workshops on sustainable gardening

## Methods & Approach

Our implementation strategy follows a phased approach with clear milestones and community engagement at every stage. We will partner with local schools, community centers, and faith-based organizations to ensure broad participation and lasting impact.

## Budget Summary

- Personnel: $21,000 (60%)
- Program Expenses: $8,750 (25%)
- Administrative Costs: $5,250 (15%)
- **Total: $35,000**

## Evaluation Plan

We will employ a mixed-methods approach including participant surveys, produce yield tracking, and community health assessments to measure program success and inform future improvements.
"""


def main():
    """Main function for the Proposal Builder page."""
    
    # Get selected grant from session state
    grant = st.session_state.get('selected_grant', {
        "title": "Community Garden Initiative Grant",
        "funder": "Green Earth Foundation",
        "deadline": "2025-03-15",
        "amount": "$10,000 - $50,000"
    })
    
    # Header
    st.markdown(f"""
        <div class="builder-header" style="color: #2d3748;">
            <h2>✍️ Proposal Builder</h2>
            <p style="color: #4a5568;">Building proposal for: <strong>{grant.get('title', 'New Proposal')}</strong></p>
            <p style="color: #718096; font-size: 0.9rem;">🏛️ {grant.get('funder', 'Unknown Funder')} | 📅 Deadline: {grant.get('deadline', 'TBD')}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Two-column layout: Agent Draft | Your Draft
    col_agent, col_user = st.columns(2)
    
    with col_agent:
        st.markdown("### 🤖 AI Agent Draft")
        st.markdown("*Generated proposal from the AI agent*")
        
        # Button to generate/regenerate agent draft
        if st.button("✨ Generate Draft", type="primary", use_container_width=True):
            with st.spinner("AI Agent is generating your proposal draft..."):
                # =============================================================================
                # API call would go here:
                # draft = get_agent_draft(grant.get('id'), project_details)
                # if draft:
                #     st.session_state.agent_draft = draft
                # =============================================================================
                
                # Using mock data for now
                import time
                time.sleep(2)  # Simulate API delay
                st.session_state.agent_draft = SAMPLE_AGENT_DRAFT
                st.rerun()
        
        # Display agent draft
        if st.session_state.agent_draft:
            st.markdown(f"""
                <div class="agent-response">
                    {st.session_state.agent_draft.replace(chr(10), '<br>')}
                </div>
            """, unsafe_allow_html=True)
            
            # Copy to user draft button
            if st.button("📋 Copy to My Draft", use_container_width=True):
                st.session_state.user_draft = st.session_state.agent_draft
                st.success("Copied to your draft!")
                st.rerun()
        else:
            st.info("Click 'Generate Draft' to get an AI-generated proposal based on the grant requirements.")
    
    with col_user:
        st.markdown("### 📝 Your Draft")
        st.markdown("*Edit and finalize your proposal*")
        
        # Editable text area for user's draft
        user_draft = st.text_area(
            "Your Proposal Draft",
            value=st.session_state.user_draft,
            height=500,
            placeholder="Start writing your proposal here, or copy the AI-generated draft and customize it...",
            label_visibility="collapsed"
        )
        
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
                label="Export",
                data=user_draft,
                file_name="draft.txt",
                mime="text/plain",
            ):
                st.success("File Downloaded!")
            copy_button(st.session_state.user_draft)
        else:
            st.warning("Nothing to export yet.")
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
