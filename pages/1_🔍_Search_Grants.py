"""
Search Grants Page - First main workflow
Allows users to search the grant database or paste grant URLs/description to find matches.
"""
import asyncio
import importlib
import json
from pathlib import Path

import streamlit as st
import sys
import os

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Page configuration
st.set_page_config(
    page_title="Search Grants | Grant Seeker AI",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display: none;}
        
        .search-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .filter-section {
            background-color: #f7fafc;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
        }
        
        .grant-card {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .grant-title {
            color: #2d3748;
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
        
        .grant-funder {
            color: #4a5568;
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
        }
        
        .grant-deadline {
            color: #e53e3e;
            font-size: 0.85rem;
            font-weight: 500;
        }
        
        .grant-amount {
            color: #38a169;
            font-size: 0.85rem;
            font-weight: 500;
        }
        
        .tag {
            display: inline-block;
            background-color: #eef6ff;
            color: #3182ce;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            margin-right: 0.5rem;
            margin-top: 0.5rem;
        }
        
        .empty-state {
            text-align: center;
            padding: 3rem;
            color: #718096;
        }
        
        .empty-state-icon {
            font-size: 4rem;
            margin-bottom: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""
if 'has_searched' not in st.session_state:
    st.session_state.has_searched = False


GRANTS_FILE_PATH = Path(__file__).resolve().parents[1] / "backend" / "grants_output.json"


@st.cache_data(show_spinner=False)
def load_grants_from_file() -> list[dict]:
    """Load grants data from the shared JSON file."""
    try:
        with GRANTS_FILE_PATH.open("r", encoding="utf-8") as fp:
            data = json.load(fp)
            if isinstance(data, list):
                return data
            st.error("Grant data file is not in the expected format. Showing empty results.")
    except FileNotFoundError:
        st.error("Grant data file not found. Please generate `backend/grants_output.json`.")
    except json.JSONDecodeError:
        st.error("Grant data file is not valid JSON. Please fix the file contents.")
    return []


def execute_grant_workflow(query: str) -> list[dict]:
    """Run the ADK workflow for the given query and persist results."""
    # Force reimport to get fresh module state
    if "adk_agent" in sys.modules:
        del sys.modules["adk_agent"]
    agent_module = importlib.import_module("adk_agent")
    
    # Create a fresh workflow instance each time
    workflow = agent_module.GrantSeekerWorkflow()

    # Run in a fresh event loop
    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(workflow.run(query))
    finally:
        loop.close()
        asyncio.set_event_loop(None)

    if results:
        workflow.save_results(results, output_file=str(GRANTS_FILE_PATH))
        load_grants_from_file.clear()
    return results


def search_grants(query, filters=None):
    """
    Search grants based on query and filters.
    First attempts to fetch from API, falls back to mock data if API unavailable.
    """
    
    # Mock data search (fallback)
    if query:
        try:
            workflow_results = execute_grant_workflow(query)
        except Exception as exc:
            st.error(f"Grant workflow failed: {exc}")
        else:
            if workflow_results:
                return workflow_results
            st.warning("Grant workflow returned no results. Showing cached data instead.")

    all_grants = load_grants_from_file()
    if not query:
        return all_grants

    query_lower = query.lower()
    results = []

    for grant in all_grants:
        # Search in title, description, tags, and funder
        title = grant.get("title", "")
        description = grant.get("description", "")
        tags = " ".join(grant.get("tags", []))
        funder = grant.get("funder", "")
        searchable = f"{title} {description} {tags} {funder}".lower()
        if query_lower in searchable:
            results.append(grant)

    return results


def render_grant_card(grant, col_key):
    """Render a single grant card."""
    title = grant.get("title", "Untitled grant")
    funder = grant.get("funder", "Unknown funder")
    deadline = grant.get("deadline", "Deadline not specified")
    amount = grant.get("amount", "Funding amount not provided")
    description = grant.get("description", "No summary available for this opportunity.")
    tags = grant.get("tags", []) or []
    grant_id = grant.get("id", f"{col_key}_{abs(hash(title))}")

    if not tags:
        tags = ["No tags available"]

    with st.container():
        st.markdown(f"""
            <div class="grant-card">
                <div class="grant-title">{title}</div>
                <div class="grant-funder">🏛️ {funder}</div>
                <div style="display: flex; gap: 1.5rem; margin: 0.5rem 0;">
                    <span class="grant-deadline">📅 Deadline: {deadline}</span>
                    <span class="grant-amount">💰 {amount}</span>
                </div>
                <p style="color: #4a5568; margin: 0.75rem 0;">{description}</p>
                <div>
                    {''.join([f'<span class="tag">{tag}</span>' for tag in tags])}
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Action buttons
        btn_col1, btn_col2 = st.columns(2)
        
        with btn_col1:
            if st.button("📋 View Details", key=f"view_{grant_id}_{col_key}", use_container_width=True):
                st.session_state.selected_grant = grant
                st.switch_page("pages/2_📋_Grant_Details.py")
        
        with btn_col2:
            if st.button("💾 Download Grant Details PDF", key=f"export_{grant_id}_{col_key}", use_container_width=True):
                st.info("Download feature coming soon!")


def main():
    """Main function for the Search Grants page."""
    
    # Header
    st.markdown("<h1 style='text-align: center;'>🔍 Search Grants</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #4a5568;'>Find relevant grant opportunities for your project</p>", unsafe_allow_html=True)
    
    # Search Section
    st.markdown("---")
    
    # Main search bar
    search_col1, search_col2 = st.columns([4, 1])
    
    with search_col1:
        search_query = st.text_input(
            "Search",
            placeholder="Enter keywords, funder name, or paste grant URL",
            label_visibility="collapsed"
        )
    
    with search_col2:
        search_clicked = st.button("🔎 Search", type="primary", use_container_width=True)
    
    
    
    # # Sort controls
    # sort_col1, sort_col2 = st.columns([3, 1])
    # with sort_col2:
    #     sort_by = st.selectbox(
    #         "Sort by",
    #         ["Relevance", "Deadline (soonest)", "Amount (highest)", "Newest"]
    #     )
    
    st.markdown("---")
    
    # Perform search only when search button is clicked
    if search_clicked:
        st.session_state.has_searched = True
        with st.spinner("Searching for grants..."):
            results = search_grants(search_query)
            st.session_state.search_results = results
            st.session_state.search_query = search_query
    
    # Results Section - only show if user has searched
    if st.session_state.has_searched:
        results = st.session_state.search_results
        
        if results:
            st.markdown(f"### Found {len(results)} grant opportunities")
            
            for i, grant in enumerate(results):
                render_grant_card(grant, f"main_{i}")
                st.markdown("<br>", unsafe_allow_html=True)
        else:
            # Empty state - no results found
            st.markdown("""
                <div class="empty-state">
                    <div class="empty-state-icon">🔍</div>
                    <h3>No grants found</h3>
                    <p>Try broader keywords or adjust your filters</p>
                    <p><strong>Suggested searches:</strong> community development, education, environmental sustainability</p>
                </div>
            """, unsafe_allow_html=True)
    else:
        # Initial state - prompt user to search
        st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">🔎</div>
                <h3>Start your search</h3>
                <p>Enter keywords above to find relevant grant opportunities</p>
                <p><strong>Try searching for:</strong> community garden, youth education, environmental research, arts & culture</p>
            </div>
        """, unsafe_allow_html=True)
    
    # Sidebar - Saved Grants
    with st.sidebar:
        st.markdown("### 💡 Search Tips")
        st.markdown("""
        - Use specific keywords related to your project
        - Try different combinations of terms
        - Include your organization type
        """)


if __name__ == "__main__":
    main()
