"""
Search Grants Page - First main workflow
Allows users to search the grant database or paste grant URLs/description to find matches.
Includes advanced filtering for Canadian grant context with mock data fallback for development.
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
from pdf_generator import generate_grant_pdf  # Used to generate PDF exports of grants

# Page configuration handled in home_page.py

# ============================================================================
# CUSTOM CSS STYLING
# ============================================================================
# Styling for the search interface including cards, filters, and empty states
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

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================
# We use session_state to persist data between page re-runs.
# This ensures that search results don't disappear when you interact with other widgets.

# Core search session state
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""
if 'has_searched' not in st.session_state:
    st.session_state.has_searched = False
if 'searching' not in st.session_state:
    st.session_state.searching = False

# Advanced filter session state - Canadian context filters
if 'demographic_focus' not in st.session_state:
    st.session_state.demographic_focus = []
if 'funding_min' not in st.session_state:
    st.session_state.funding_min = None
if 'funding_max' not in st.session_state:
    st.session_state.funding_max = None
if 'funding_types' not in st.session_state:
    st.session_state.funding_types = []
if 'geographic_scope' not in st.session_state:
    st.session_state.geographic_scope = ""
if 'applicant_type' not in st.session_state:
    st.session_state.applicant_type = ""
if 'project_stage' not in st.session_state:
    st.session_state.project_stage = ""


GRANTS_FILE_PATH = Path(__file__).resolve().parents[1] / "backend" / "grants_output.json"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def has_active_filters():
    """
    Check if any advanced filters are currently active.
    Returns True if user has selected any filter, False if all filters are empty/default.
    Used to determine whether to show mock data (filters active) or real search (no filters).
    """
    return (
        bool(st.session_state.demographic_focus) or
        st.session_state.funding_min is not None or
        st.session_state.funding_max is not None or
        bool(st.session_state.funding_types) or
        bool(st.session_state.geographic_scope) or
        bool(st.session_state.applicant_type) or
        bool(st.session_state.project_stage)
    )


def generate_mock_canadian_grants(filters, query):
    """
    Generate mock Canadian grant data for development purposes.
    
    When users enable advanced filters, this function returns realistic placeholder grants
    instead of making real backend calls. This allows developers to test the filtering UI
    without waiting for the actual agent workflow to complete.
    
    Args:
        filters: Dictionary containing all active filter selections
        query: User's search query text
    
    Returns:
        List of 5-8 mock grant dictionaries with Canadian context data
    """
    import random
    
    # Realistic Canadian grant funders
    funders = [
        "Natural Sciences and Engineering Research Council of Canada (NSERC)",
        "Social Sciences and Humanities Research Council (SSHRC)",
        "Innovation, Science and Economic Development Canada",
        "Canada Council for the Arts",
        "Ontario Trillium Foundation",
        "Business Development Bank of Canada (BDC)",
        "Indigenous Services Canada",
        "Women and Gender Equality Canada",
        "Regional Development Agencies (FedDev Ontario)",
        "British Columbia Arts Council"
    ]
    
    # Variety of Canadian grant program titles
    grant_titles = [
        "Indigenous Innovation Fund",
        "Women Entrepreneurs Program",
        "Clean Technology Research Grant",
        "Community Development Initiative",
        "Youth Employment and Skills Strategy",
        "Rural Economic Development Program",
        "Digital Technology Adoption Program",
        "Sustainable Agriculture Innovation Grant",
        "Arts and Culture Creation Fund",
        "Export Market Development Program",
        "Social Enterprise Support Grant",
        "Northern Economic Development Fund"
    ]
    
    # Varied deadline options
    deadlines = [
        "March 31, 2026",
        "April 15, 2026",
        "May 1, 2026",
        "June 30, 2026",
        "Rolling intake",
        "February 28, 2026"
    ]
    
    # Realistic funding amounts in Canadian dollars
    amounts = [
        "$5,000 - $25,000",
        "$10,000 - $50,000",
        "$25,000 - $100,000",
        "$50,000 - $250,000",
        "Up to $500,000",
        "$15,000 - $75,000"
    ]
    
    # Generic but realistic grant descriptions
    descriptions = [
        "This program supports innovative projects that address community needs and promote sustainable development across Canada.",
        "Funding is available for organizations committed to advancing diversity, equity, and inclusion in their operations and programming.",
        "This initiative provides non-repayable contributions to eligible applicants pursuing research and development in emerging technologies.",
        "Support for early-stage ventures and social enterprises focused on creating positive social and environmental impact.",
        "Designed to help organizations expand their operations, hire skilled workers, and access new markets domestically and internationally.",
        "This program offers financial assistance for projects that strengthen community capacity and improve quality of life for residents."
    ]
    
    # Tags that might match various filter selections
    tag_options = [
        ["Women-led", "Technology", "Innovation"],
        ["Indigenous", "Community Development", "Capacity Building"],
        ["Youth", "Employment", "Training"],
        ["Environmental", "Sustainability", "Research"],
        ["Arts", "Culture", "Creative Industries"],
        ["Export", "Trade", "International"],
        ["Rural", "Northern", "Remote Communities"],
        ["BIPOC", "Diversity", "Equity"]
    ]
    
    # Generate 5-8 random grants for realistic variety
    num_grants = random.randint(5, 8)
    mock_grants = []
    
    for i in range(num_grants):
        grant = {
            "id": f"mock_canadian_{i+1}",  # Unique identifier
            "title": random.choice(grant_titles),
            "funder": random.choice(funders),
            "deadline": random.choice(deadlines),
            "amount": random.choice(amounts),
            "description": random.choice(descriptions),
            "tags": random.choice(tag_options),
            "url": f"https://grants.canada.ca/mock-grant-{i+1}",
            "eligibility": "Open to Canadian organizations and individuals meeting specific criteria",
            "application_process": "Online application through the funder's portal"
        }
        mock_grants.append(grant)
    
    return mock_grants




# ============================================================================
# DATA LOADING & CACHING
# ============================================================================

@st.cache_data(show_spinner=False)
def load_grants_from_file() -> list[dict]:
    """
    Load grants data from the shared JSON file with caching.
    
    This function reads from backend/grants_output.json which is populated by
    the adk_agent workflow. Streamlit caches the results to avoid repeated file I/O.
    
    Returns:
        List of grant dictionaries, or empty list if file doesn't exist or is invalid
    """
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
    """
    Run the ADK workflow for the given query and persist results.
    
    This function:
    1. Imports the adk_agent module (forcing a fresh import)
    2. Creates a new GrantSeekerWorkflow instance
    3. Runs the workflow asynchronously with the user's query
    4. Saves results to a shared JSON file for access by other pages
    
    Args:
        query: User's search query for finding relevant grants
    
    Returns:
        List of grant results from the workflow, or empty list if workflow fails
    """
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
        # Save results to a shared JSON file so other pages can access them if needed
        workflow.save_results(results, output_file=str(GRANTS_FILE_PATH))
        load_grants_from_file.clear()
    return results


def search_grants(query, filters=None):
    """
    Search grants based on query and filters.
    
    Logic flow:
    1. If advanced filters are active → return mock Canadian grants (dev mode)
    2. If query provided → run ADK agent workflow for real search
    3. If no query → return all grants from file as fallback
    
    This allows developers to test filter UI without waiting for agent execution,
    while preserving normal search behavior when no filters are selected.
    
    Args:
        query: Search keywords entered by user
        filters: Dictionary containing all filter selections from advanced filters section
    
    Returns:
        List of grant dictionaries matching the search criteria
    """
    
    # Check if advanced filters are active - use mock data for development
    if filters and has_active_filters():
        return generate_mock_canadian_grants(filters, query)
    
    # If user provided a search query, run the real workflow agent
    if query:
        try:
            workflow_results = execute_grant_workflow(query)
        except Exception as exc:
            st.error(f"Grant workflow failed: {exc}")
        else:
            if workflow_results:
                return workflow_results
            st.warning("Grant workflow returned no results. Showing cached data instead.")

    # Fallback: Load all grants from cached file
    all_grants = load_grants_from_file()
    if not query:
        return all_grants

    # Search through cached grants using basic text matching
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


# ============================================================================
# UI RENDERING FUNCTIONS
# ============================================================================


def render_grant_card(grant, col_key):
    """
    Render a single grant card with styling and action buttons.
    
    Creates a visual card for each grant showing:
    - Title, funder, deadline, and funding amount
    - Description and relevant tags
    - "View Details" button to navigate to grant details page
    - "Download PDF" button to export grant information
    
    Args:
        grant: Dictionary containing grant data
        col_key: Unique identifier for the card to prevent Streamlit key conflicts
    """
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
                st.switch_page("frontend/grant_details.py")
        
        with btn_col2:
            pdf_data = generate_grant_pdf(grant)
            st.download_button(
                label="💾 Download PDF",
                data=pdf_data,
                file_name=f"grant_{grant_id}.pdf",
                mime="application/pdf",
                key=f"export_{grant_id}_{col_key}",
                use_container_width=True
            )


def main():
    """
    Main function for the Search Grants page.
    
    Page structure:
    1. Header with title and description
    2. Search bar with primary search button
    3. Advanced Filters expander (collapsible section)
       - Demographic Focus (multi-select)
       - Funding Amount Range (min/max inputs)
       - Funding Type (multi-select)
       - Geographic Scope (dropdown)
       - Applicant Type (dropdown)
       - Project Stage (dropdown)
       - Clear All Filters button
    4. Results section showing grant cards or empty state
    5. Sidebar with search tips
    """
    
    # Header
    col_back, col_title = st.columns([1, 5])
            
    with col_title:
        st.markdown("<h1 style='text-align: center; margin-top: -1rem;'>🔍 Search Grants</h1>", unsafe_allow_html=True)
    
    st.markdown("<p style='text-align: center; color: #4a5568;'>Find relevant grant opportunities for your project</p>", unsafe_allow_html=True)
    
    # Search Section
    st.markdown("---")
    
    # Main search bar with button
    search_col1, search_col2 = st.columns([4, 1])
    
    with search_col1:
        search_query = st.text_input(
            "Search",
            placeholder="Enter keywords, funder name, or paste grant URL",
            label_visibility="collapsed"
        )
    
    with search_col2:
        search_clicked = st.button(
            "🔎 Search" if not st.session_state.searching else "⏳ Searching...", 
            type="primary", 
            use_container_width=True,
            disabled=st.session_state.searching
        )
    
    # ========================================================================
    # ADVANCED FILTERS SECTION (Collapsible Expander)
    # ========================================================================
    # Users can enable any filter to trigger mock data mode for development.
    # The expander keeps the UI clean by hiding filters by default.
    with st.expander("🔧 Advanced Filters (Canadian Context)", expanded=False):
        
        # FILTER 1: Demographic Focus (Multi-select)
        # Users can select multiple demographic categories. Using key for automatic state binding.
        st.markdown("**🎯 Demographic Focus**")
        demographic_options = [
            "Women-led / Female Founders",
            "Indigenous-led (First Nations, Inuit, Métis)",
            "Black-led",
            "BIPOC (General)",
            "Youth-led (Under 30)",
            "Newcomers to Canada"
        ]
        st.multiselect(
            "Select demographic focus",
            demographic_options,
            key="demographic_focus",
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # FILTER 2: Funding Amount (Range with Min/Max inputs)
        # Users set budget constraints. Values of 0 are treated as "not set"
        st.markdown("**💰 Funding Amount Range**")
        col_min, col_max = st.columns(2)
        with col_min:
            funding_min = st.number_input(
                "Minimum ($)",
                min_value=0,
                max_value=10000000,
                value=st.session_state.funding_min if st.session_state.funding_min is not None else 0,
                step=5000,
                format="%d"
            )
            st.session_state.funding_min = funding_min if funding_min > 0 else None
        
        with col_max:
            funding_max = st.number_input(
                "Maximum ($)",
                min_value=0,
                max_value=10000000,
                value=st.session_state.funding_max if st.session_state.funding_max is not None else 0,
                step=5000,
                format="%d"
            )
            st.session_state.funding_max = funding_max if funding_max > 0 else None
        
        st.markdown("---")
        
        # Row 3: Funding Type
        # Users can filter by how the grant is structured (grant vs loan vs tax credit, etc)
        st.markdown("**📝 Funding Type**")
        funding_type_options = [
            "Non-repayable Grant",
            "Repayable Loan / Contribution",
            "Tax Credit",
            "Wage Subsidy (Hiring grants)",
            "In-Kind (Services/Equipment)"
        ]
        st.multiselect(
            "Select funding types",
            funding_type_options,
            key="funding_types",
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # FILTERS 4 & 5: Geographic Scope and Applicant Type (Side-by-side dropdowns)
        # Geographic scope allows targeting specific provinces or national programs
        # Applicant type filters by organization structure (nonprofit vs for-profit, etc)
        col_geo, col_app = st.columns(2)
        
        with col_geo:
            st.markdown("**🌍 Geographic Scope**")
            geographic_options = [
                "",
                "National (Federal Canada-wide)",
                "Alberta",
                "British Columbia",
                "Manitoba",
                "New Brunswick",
                "Newfoundland and Labrador",
                "Northwest Territories",
                "Nova Scotia",
                "Nunavut",
                "Ontario",
                "Prince Edward Island",
                "Quebec",
                "Saskatchewan",
                "Yukon",
                "Rural / Remote (Northern/Rural streams)"
            ]
            st.session_state.geographic_scope = st.selectbox(
                "Select geographic scope",
                geographic_options,
                index=geographic_options.index(st.session_state.geographic_scope) if st.session_state.geographic_scope in geographic_options else 0,
                label_visibility="collapsed"
            )
        
        with col_app:
            st.markdown("**🏢 Applicant Type**")
            applicant_options = [
                "",
                "Registered Non-profit / Charity",
                "For-profit / Startup",
                "Academic / Research Institution",
                "Individual / Artist"
            ]
            st.session_state.applicant_type = st.selectbox(
                "Select applicant type",
                applicant_options,
                index=applicant_options.index(st.session_state.applicant_type) if st.session_state.applicant_type in applicant_options else 0,
                label_visibility="collapsed"
            )
        
        st.markdown("---")
        
        # FILTER 6: Project Stage (Dropdown)
        # Filter by the maturity/stage of the applicant's project
        st.markdown("**🚀 Project Stage**")
        project_stage_options = [
            "",
            "Early Stage / R&D",
            "Commercialization / Scaling",
            "Hiring / Training",
            "Export / International Expansion"
        ]
        st.session_state.project_stage = st.selectbox(
            "Select project stage",
            project_stage_options,
            index=project_stage_options.index(st.session_state.project_stage) if st.session_state.project_stage in project_stage_options else 0,
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Clear All Filters button - resets all filter selections to default values
        if st.button("🗑️ Clear All Filters", use_container_width=True):
            st.session_state.demographic_focus = []
            st.session_state.funding_min = None
            st.session_state.funding_max = None
            st.session_state.funding_types = []
            st.session_state.geographic_scope = ""
            st.session_state.applicant_type = ""
            st.session_state.project_stage = ""
            st.rerun()
        
        # Show active filters indicator with count
        # Displays when user has selected any filters, notifying them about mock data mode
        if has_active_filters():
            active_count = sum([
                1 if st.session_state.demographic_focus else 0,
                1 if st.session_state.funding_min is not None or st.session_state.funding_max is not None else 0,
                1 if st.session_state.funding_types else 0,
                1 if st.session_state.geographic_scope else 0,
                1 if st.session_state.applicant_type else 0,
                1 if st.session_state.project_stage else 0
            ])
            st.info(f"✅ {active_count} filter(s) active - Using mock Canadian grant data for development")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ========================================================================
    # SEARCH EXECUTION
    # ========================================================================
    # Triggered when user clicks the Search button
    # ========================================================================
    # SEARCH EXECUTION
    # ========================================================================
    # Triggered when user clicks the Search button
    if search_clicked:
        st.session_state.searching = True
        st.session_state.has_searched = True
        st.rerun()
    
    # Execute the search when in searching state
    # Prepares filter dictionary and calls search_grants() function
    if st.session_state.searching:
        with st.spinner("Searching for grants..."):
            # Prepare filters dictionary
            filters = {
                'demographic_focus': st.session_state.demographic_focus,
                'funding_min': st.session_state.funding_min,
                'funding_max': st.session_state.funding_max,
                'funding_types': st.session_state.funding_types,
                'geographic_scope': st.session_state.geographic_scope,
                'applicant_type': st.session_state.applicant_type,
                'project_stage': st.session_state.project_stage
            }
            results = search_grants(search_query, filters)
            st.session_state.search_results = results
            st.session_state.search_query = search_query
            st.session_state.searching = False
            st.rerun()
    
    # ========================================================================
    # RESULTS DISPLAY SECTION
    # ========================================================================
    # Only show results if user has performed a search
    if st.session_state.has_searched:
        results = st.session_state.search_results
        
        if results:
            # Display number of results found
            st.markdown(f"### Found {len(results)} grant opportunities")
            
            # Render each grant as a card with action buttons
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
        # Shows helpful suggestions before user performs their first search
        st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">🔎</div>
                <h3>Start your search</h3>
                <p>Enter keywords above to find relevant grant opportunities</p>
                <p><strong>Try searching for:</strong> community garden, youth education, environmental research, arts & culture</p>
            </div>
        """, unsafe_allow_html=True)
    
    # ========================================================================
    # SIDEBAR - SEARCH TIPS
    # ========================================================================
    # Provides helpful guidance for effective search queries
    with st.sidebar:
        st.markdown("### 💡 Search Tips")
        st.markdown("""
        - Use specific keywords related to your project
        - Try different combinations of terms
        - Include your organization type
        """)


if __name__ == "__main__":
    main()
