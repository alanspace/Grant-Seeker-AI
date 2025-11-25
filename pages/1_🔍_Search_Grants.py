"""
Search Grants Page - First main workflow
Allows users to search the grant database or paste grant URLs/description to find matches.
"""
import streamlit as st
import sys
import os

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Page configuration
st.set_page_config(
    page_title="Search Grants | Grant Seeker's Co-Pilot",
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

# Sample grant data for demonstration
SAMPLE_GRANTS = [
    {
        "id": 1,
        "title": "Community Garden Initiative Grant",
        "funder": "Green Earth Foundation",
        "deadline": "2025-03-15",
        "amount": "$10,000 - $50,000",
        "description": "Supporting community-based urban agriculture projects that promote food security and environmental education.",
        "tags": ["Environment", "Community", "Agriculture"],
        "eligibility": "Non-profit organizations, community groups",
        "url": "https://example.com/grant1"
    },
    {
        "id": 2,
        "title": "Youth Education & Development Fund",
        "funder": "Future Leaders Foundation",
        "deadline": "2025-04-01",
        "amount": "$5,000 - $25,000",
        "description": "Funding innovative programs that empower young people through education, mentorship, and skill development.",
        "tags": ["Education", "Youth", "Development"],
        "eligibility": "501(c)(3) organizations",
        "url": "https://example.com/grant2"
    },
    {
        "id": 3,
        "title": "Environmental Sustainability Research Grant",
        "funder": "National Science Council",
        "deadline": "2025-05-30",
        "amount": "$50,000 - $200,000",
        "description": "Supporting research projects focused on environmental sustainability, climate action, and conservation.",
        "tags": ["Research", "Environment", "Sustainability"],
        "eligibility": "Universities, research institutions",
        "url": "https://example.com/grant3"
    },
    {
        "id": 4,
        "title": "Small Business Innovation Grant",
        "funder": "Economic Development Agency",
        "deadline": "2025-02-28",
        "amount": "$25,000 - $100,000",
        "description": "Supporting small businesses developing innovative solutions for social and environmental challenges.",
        "tags": ["Innovation", "Business", "Social Impact"],
        "eligibility": "Small businesses, startups",
        "url": "https://example.com/grant4"
    },
    {
        "id": 5,
        "title": "Arts & Culture Community Grant",
        "funder": "Creative Arts Foundation",
        "deadline": "2025-06-15",
        "amount": "$2,500 - $15,000",
        "description": "Funding community arts projects that celebrate diversity, promote cultural exchange, and engage local communities.",
        "tags": ["Arts", "Culture", "Community"],
        "eligibility": "Non-profits, arts organizations",
        "url": "https://example.com/grant5"
    }
]


def search_grants(query, filters=None):
    """Search grants based on query and filters."""
    if not query:
        return SAMPLE_GRANTS
    
    query_lower = query.lower()
    results = []
    
    for grant in SAMPLE_GRANTS:
        # Search in title, description, tags, and funder
        searchable = f"{grant['title']} {grant['description']} {' '.join(grant['tags'])} {grant['funder']}".lower()
        if query_lower in searchable:
            results.append(grant)
    
    return results


def render_grant_card(grant, col_key):
    """Render a single grant card."""
    with st.container():
        st.markdown(f"""
            <div class="grant-card">
                <div class="grant-title">{grant['title']}</div>
                <div class="grant-funder">🏛️ {grant['funder']}</div>
                <div style="display: flex; gap: 1.5rem; margin: 0.5rem 0;">
                    <span class="grant-deadline">📅 Deadline: {grant['deadline']}</span>
                    <span class="grant-amount">💰 {grant['amount']}</span>
                </div>
                <p style="color: #4a5568; margin: 0.75rem 0;">{grant['description']}</p>
                <div>
                    {''.join([f'<span class="tag">{tag}</span>' for tag in grant['tags']])}
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Action buttons
        btn_col1, btn_col2 = st.columns(2)
        
        with btn_col1:
            if st.button("📋 View Details", key=f"view_{grant['id']}_{col_key}", use_container_width=True):
                st.session_state.selected_grant = grant
                st.switch_page("pages/2_📋_Grant_Details.py")
        
        with btn_col2:
            if st.button("✍️ Start Proposal", key=f"proposal_{grant['id']}_{col_key}", use_container_width=True):
                st.session_state.selected_grant = grant
                st.switch_page("pages/3_✍️_Proposal_Builder.py")


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
    
    
    
    # Sort controls
    sort_col1, sort_col2 = st.columns([3, 1])
    with sort_col2:
        sort_by = st.selectbox(
            "Sort by",
            ["Relevance", "Deadline (soonest)", "Amount (highest)", "Newest"]
        )
    
    st.markdown("---")
    
    # Perform search
    if search_clicked or search_query:
        with st.spinner("Searching for grants..."):
            results = search_grants(search_query)
            st.session_state.search_results = results
            st.session_state.search_query = search_query
    else:
        # Show all grants by default
        st.session_state.search_results = SAMPLE_GRANTS
    
    # Results Section
    results = st.session_state.search_results
    
    if results:
        st.markdown(f"### Found {len(results)} grant opportunities")
        
        for i, grant in enumerate(results):
            render_grant_card(grant, f"main_{i}")
            st.markdown("<br>", unsafe_allow_html=True)
    else:
        # Empty state
        st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">🔍</div>
                <h3>No grants found</h3>
                <p>Try broader keywords or adjust your filters</p>
                <p><strong>Suggested searches:</strong> community development, education, environmental sustainability</p>
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
