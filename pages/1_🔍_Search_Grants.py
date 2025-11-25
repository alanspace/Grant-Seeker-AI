"""
Search Grants Page - First main workflow
Allows users to search the grant database or paste grant URLs/description to find matches.
"""
import streamlit as st
import sys
import os
import time

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Page configuration
st.set_page_config(
    page_title="Search Grants | Grant Seeker's Co-Pilot",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =============================================================================
# API INTEGRATION (Commented - uncomment when API is available)
# =============================================================================
# import requests
# 
# API_BASE_URL = "https://your-api-endpoint.com/api/v1"
# 
# def fetch_grants_from_api(query: str, filters: dict = None) -> list:
#     """
#     Fetch grants from the API based on search query and filters.
#     
#     Args:
#         query: Search query string
#         filters: Optional dictionary of filters (funding_type, eligibility, geography, etc.)
#     
#     Returns:
#         List of grant objects in the format:
#         {
#             "id": int,
#             "title": str,
#             "funder": str,
#             "deadline": str (YYYY-MM-DD),
#             "amount": str,
#             "description": str,
#             "detailed_overview": str,
#             "tags": list[str],
#             "eligibility": str,
#             "url": str,
#             "application_requirements": list[str],
#             "funding_type": str,
#             "geography": str,
#             "key_dates": list[dict],  # [{"event": str, "date": str}, ...]
#             "risk_factors": list[str],
#             "fit_score": int (0-100),
#             "eligibility_checklist": list[dict]  # [{"item": str, "met": bool|None, "confidence": str}, ...]
#         }
#     """
#     try:
#         params = {"q": query}
#         if filters:
#             params.update(filters)
#         
#         response = requests.get(f"{API_BASE_URL}/grants/search", params=params, timeout=30)
#         response.raise_for_status()
#         
#         data = response.json()
#         return data.get("grants", [])
#     
#     except requests.RequestException as e:
#         st.error(f"Failed to fetch grants from API: {str(e)}")
#         return None  # Return None to indicate API failure, triggering fallback to mock data
# =============================================================================

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

# Sample grant data for demonstration (used as fallback when API is unavailable)
SAMPLE_GRANTS = [
    {
        "id": 1,
        "title": "Community Garden Initiative Grant",
        "funder": "Green Earth Foundation",
        "deadline": "2025-03-15",
        "amount": "$10,000 - $50,000",
        "description": "Supporting community-based urban agriculture projects that promote food security and environmental education.",
        "detailed_overview": "The Community Garden Initiative Grant supports organizations working to establish and expand community gardens in urban areas. This funding opportunity is designed to help communities create sustainable food sources, provide educational opportunities about agriculture and nutrition, and build stronger neighborhood connections through shared gardening spaces. Priority is given to projects serving food-insecure communities and those incorporating youth education programs.",
        "tags": ["Environment", "Community", "Agriculture"],
        "eligibility": "Non-profit organizations, community groups",
        "url": "https://example.com/grant1",
        "application_requirements": [
            "501(c)(3) determination letter",
            "Project budget",
            "Implementation timeline",
            "Letters of support"
        ],
        "funding_type": "Grant",
        "geography": "United States",
        "key_dates": [
            {"event": "Application opens", "date": "2025-01-15"},
            {"event": "Letter of Intent due", "date": "2025-02-01"},
            {"event": "Full application deadline", "date": "2025-03-15"},
            {"event": "Award notification", "date": "2025-05-01"},
            {"event": "Grant period begins", "date": "2025-06-01"}
        ],
        "risk_factors": [
            "Competitive grant with ~15% acceptance rate",
            "Requires detailed evaluation plan",
            "Matching funds may be required"
        ],
        "fit_score": 85,
        "eligibility_checklist": [
            {"item": "501(c)(3) Non-profit status", "met": True, "confidence": "high"},
            {"item": "Operational for at least 2 years", "met": True, "confidence": "high"},
            {"item": "Annual budget under $1M", "met": None, "confidence": "medium"},
            {"item": "Located in eligible geographic area", "met": True, "confidence": "high"},
            {"item": "Previous grant recipient status", "met": None, "confidence": "low"}
        ]
    },
    {
        "id": 2,
        "title": "Youth Education & Development Fund",
        "funder": "Future Leaders Foundation",
        "deadline": "2025-04-01",
        "amount": "$5,000 - $25,000",
        "description": "Funding innovative programs that empower young people through education, mentorship, and skill development.",
        "detailed_overview": "The Youth Education & Development Fund seeks to support innovative educational programs that prepare young people for success in the 21st century. We prioritize projects that focus on STEM education, leadership development, career readiness, and social-emotional learning. Successful applicants will demonstrate a clear theory of change and measurable outcomes for participating youth.",
        "tags": ["Education", "Youth", "Development"],
        "eligibility": "501(c)(3) organizations",
        "url": "https://example.com/grant2",
        "application_requirements": [
            "Organizational budget",
            "Program description",
            "Evaluation plan",
            "Staff qualifications"
        ],
        "funding_type": "Grant",
        "geography": "United States",
        "key_dates": [
            {"event": "Application opens", "date": "2025-02-01"},
            {"event": "Full application deadline", "date": "2025-04-01"},
            {"event": "Award notification", "date": "2025-05-15"},
            {"event": "Grant period begins", "date": "2025-07-01"}
        ],
        "risk_factors": [
            "Requires detailed evaluation metrics",
            "Strong preference for established programs"
        ],
        "fit_score": 78,
        "eligibility_checklist": [
            {"item": "501(c)(3) Non-profit status", "met": True, "confidence": "high"},
            {"item": "Youth-serving organization", "met": True, "confidence": "high"},
            {"item": "Demonstrated track record", "met": None, "confidence": "medium"}
        ]
    },
    {
        "id": 3,
        "title": "Environmental Sustainability Research Grant",
        "funder": "National Science Council",
        "deadline": "2025-05-30",
        "amount": "$50,000 - $200,000",
        "description": "Supporting research projects focused on environmental sustainability, climate action, and conservation.",
        "detailed_overview": "The Environmental Sustainability Research Grant funds cutting-edge research addressing critical environmental challenges including climate change mitigation, biodiversity conservation, sustainable resource management, and environmental justice. We seek proposals that bridge scientific research with practical applications and community engagement.",
        "tags": ["Research", "Environment", "Sustainability"],
        "eligibility": "Universities, research institutions",
        "url": "https://example.com/grant3",
        "application_requirements": [
            "Research proposal",
            "Budget justification",
            "CV of principal investigator",
            "Institutional support letter"
        ],
        "funding_type": "Research Grant",
        "geography": "International",
        "key_dates": [
            {"event": "Application opens", "date": "2025-03-01"},
            {"event": "Full application deadline", "date": "2025-05-30"},
            {"event": "Peer review period", "date": "2025-06-15"},
            {"event": "Award notification", "date": "2025-08-01"}
        ],
        "risk_factors": [
            "Highly competitive - 10% acceptance rate",
            "Requires preliminary data",
            "Multi-year commitment expected"
        ],
        "fit_score": 65,
        "eligibility_checklist": [
            {"item": "Academic institution affiliation", "met": None, "confidence": "medium"},
            {"item": "PhD-level principal investigator", "met": None, "confidence": "low"},
            {"item": "IRB approval if applicable", "met": None, "confidence": "medium"}
        ]
    },
    {
        "id": 4,
        "title": "Small Business Innovation Grant",
        "funder": "Economic Development Agency",
        "deadline": "2025-02-28",
        "amount": "$25,000 - $100,000",
        "description": "Supporting small businesses developing innovative solutions for social and environmental challenges.",
        "detailed_overview": "The Small Business Innovation Grant supports entrepreneurs and small businesses creating innovative products, services, or technologies that address pressing social or environmental challenges. We seek ventures with scalable solutions that demonstrate both commercial viability and positive community impact.",
        "tags": ["Innovation", "Business", "Social Impact"],
        "eligibility": "Small businesses, startups",
        "url": "https://example.com/grant4",
        "application_requirements": [
            "Business plan",
            "Financial statements",
            "Innovation description",
            "Market analysis"
        ],
        "funding_type": "Grant",
        "geography": "United States",
        "key_dates": [
            {"event": "Application opens", "date": "2025-01-01"},
            {"event": "Full application deadline", "date": "2025-02-28"},
            {"event": "Award notification", "date": "2025-04-15"}
        ],
        "risk_factors": [
            "Requires proof of concept",
            "Must demonstrate market potential"
        ],
        "fit_score": 72,
        "eligibility_checklist": [
            {"item": "Registered small business", "met": None, "confidence": "medium"},
            {"item": "Less than 50 employees", "met": None, "confidence": "low"},
            {"item": "Innovative product or service", "met": None, "confidence": "medium"}
        ]
    },
    {
        "id": 5,
        "title": "Arts & Culture Community Grant",
        "funder": "Creative Arts Foundation",
        "deadline": "2025-06-15",
        "amount": "$2,500 - $15,000",
        "description": "Funding community arts projects that celebrate diversity, promote cultural exchange, and engage local communities.",
        "detailed_overview": "The Arts & Culture Community Grant supports arts projects that strengthen community bonds, celebrate cultural diversity, and make the arts accessible to underserved populations. We fund a wide range of artistic disciplines including visual arts, performing arts, literary arts, and multimedia projects that engage communities in meaningful ways.",
        "tags": ["Arts", "Culture", "Community"],
        "eligibility": "Non-profits, arts organizations",
        "url": "https://example.com/grant5",
        "application_requirements": [
            "Project description",
            "Artist portfolio",
            "Community engagement plan",
            "Budget"
        ],
        "funding_type": "Grant",
        "geography": "Local/State",
        "key_dates": [
            {"event": "Application opens", "date": "2025-04-01"},
            {"event": "Full application deadline", "date": "2025-06-15"},
            {"event": "Award notification", "date": "2025-07-30"}
        ],
        "risk_factors": [
            "Geographic restrictions may apply",
            "Requires community partnership letters"
        ],
        "fit_score": 80,
        "eligibility_checklist": [
            {"item": "Arts-focused organization", "met": None, "confidence": "medium"},
            {"item": "Community engagement component", "met": True, "confidence": "high"},
            {"item": "Located in eligible region", "met": None, "confidence": "low"}
        ]
    }
]


def search_grants(query, filters=None):
    """
    Search grants based on query and filters.
    First attempts to fetch from API, falls back to mock data if API unavailable.
    """
    # =============================================================================
    # API Integration (Uncomment when API is available)
    # =============================================================================
    # api_results = fetch_grants_from_api(query, filters)
    # if api_results is not None:
    #     return api_results
    # 
    # # If API fails, fall back to mock data
    # st.warning("Unable to connect to grant database. Showing sample data.")
    # =============================================================================
    
    # Mock data search (fallback)
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
            # Simulate API delay for demo purposes
            time.sleep(1)
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
