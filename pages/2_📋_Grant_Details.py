"""
Grant Details Page - Show full metadata and extracted eligibility/requirements
"""
import streamlit as st
import sys
import os

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Page configuration
st.set_page_config(
    page_title="Grant Details | Grant Seeker's Co-Pilot",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display: none;}
        
        .detail-header {
            background-color: #eef6ff;
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 2rem;
        }
        
        .detail-title {
            font-size: 1.8rem;
            font-weight: 700;
            color: #2d3748;
            margin-bottom: 0.5rem;
        }
        
        .detail-funder {
            font-size: 1.1rem;
            color: #4a5568;
            margin-bottom: 1rem;
        }
        
        .detail-meta {
            display: flex;
            gap: 2rem;
            flex-wrap: wrap;
            margin-top: 1rem;
        }
        
        .meta-item {
            background-color: #ffffff;
            padding: 0.75rem 1.25rem;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .meta-label {
            color: #718096;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .meta-value {
            color: #2d3748;
            font-size: 1rem;
            font-weight: 600;
        }
        
        .insight-card {
            background-color: #f7fafc;
            border-left: 4px solid #3182ce;
            padding: 1rem 1.5rem;
            margin: 1rem 0;
            border-radius: 0 8px 8px 0;
        }
        
        .checklist-item {
            display: flex;
            align-items: center;
            padding: 0.5rem 0;
            border-bottom: 1px solid #e2e8f0;
        }
        
        .checklist-check {
            color: #38a169;
            margin-right: 0.75rem;
        }
        
        .checklist-x {
            color: #e53e3e;
            margin-right: 0.75rem;
        }
        
        .confidence-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 500;
        }
        
        .confidence-high {
            background-color: #c6f6d5;
            color: #276749;
        }
        
        .confidence-medium {
            background-color: #feebc8;
            color: #c05621;
        }
        
        .confidence-low {
            background-color: #fed7d7;
            color: #c53030;
        }
    </style>
""", unsafe_allow_html=True)

# Sample extracted insights (simulating AI analysis)
# These will be populated from API data when available
DEFAULT_INSIGHTS = {
    "eligibility_checklist": [
        {"item": "501(c)(3) Non-profit status", "met": True, "confidence": "high"},
        {"item": "Operational for at least 2 years", "met": True, "confidence": "high"},
        {"item": "Annual budget under $1M", "met": None, "confidence": "medium"},
        {"item": "Located in eligible geographic area", "met": True, "confidence": "high"},
        {"item": "Previous grant recipient status", "met": None, "confidence": "low"}
    ],
    "required_documents": [
        "Letter of Determination (501(c)(3))",
        "Current year operating budget",
        "Most recent audited financial statements",
        "Board of Directors list",
        "Project budget and narrative",
        "Two letters of support from community partners"
    ],
    "key_dates": [
        {"event": "Application opens", "date": "2025-01-15"},
        {"event": "Letter of Intent due", "date": "2025-02-01"},
        {"event": "Full application deadline", "date": "2025-03-15"},
        {"event": "Award notification", "date": "2025-05-01"},
        {"event": "Grant period begins", "date": "2025-06-01"}
    ],
    "fit_score": 85,
    "risk_factors": [
        "Competitive grant with ~15% acceptance rate",
        "Requires detailed evaluation plan",
        "Matching funds may be required"
    ]
}


def get_confidence_badge(confidence):
    """Return HTML for confidence badge."""
    colors = {
        "high": "confidence-high",
        "medium": "confidence-medium",
        "low": "confidence-low"
    }
    return f'<span class="confidence-badge {colors.get(confidence, "confidence-medium")}">{confidence.title()} confidence</span>'


def render_eligibility_checklist(items):
    """Render the eligibility checklist."""
    for item in items:
        status = item.get("met")
        if status is True:
            icon = "✅"
            status_class = "checklist-check"
        elif status is False:
            icon = "❌"
            status_class = "checklist-x"
        else:
            icon = "❓"
            status_class = ""
        
        st.markdown(f"""
            <div class="checklist-item">
                <span class="{status_class}">{icon}</span>
                <span>{item['item']}</span>
                <span style="margin-left: auto;">{get_confidence_badge(item['confidence'])}</span>
            </div>
        """, unsafe_allow_html=True)


def main():
    """Main function for the Grant Details page."""
    
    # Get selected grant from session state or use default
    grant = st.session_state.get('selected_grant', {
        "id": 1,
        "title": "Community Garden Initiative Grant",
        "funder": "Green Earth Foundation",
        "deadline": "2025-03-15",
        "amount": "$10,000 - $50,000",
        "description": "Supporting community-based urban agriculture projects that promote food security and environmental education.",
        "detailed_overview": "The Community Garden Initiative Grant supports organizations working to establish and expand community gardens in urban areas.",
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
    })
    
    # Get insights from grant data (API format) or fall back to defaults
    fit_score = grant.get('fit_score', DEFAULT_INSIGHTS['fit_score'])
    key_dates = grant.get('key_dates', DEFAULT_INSIGHTS['key_dates'])
    risk_factors = grant.get('risk_factors', DEFAULT_INSIGHTS['risk_factors'])
    eligibility_checklist = grant.get('eligibility_checklist', DEFAULT_INSIGHTS['eligibility_checklist'])
    application_requirements = grant.get('application_requirements', DEFAULT_INSIGHTS['required_documents'])
    
    # Header Section
    st.markdown(f"""
        <div class="detail-header">
            <div class="detail-title">{grant['title']}</div>
            <div class="detail-funder">🏛️ {grant['funder']}</div>
            <div class="detail-meta">
                <div class="meta-item">
                    <div class="meta-label">Deadline</div>
                    <div class="meta-value">📅 {grant['deadline']}</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">Amount</div>
                    <div class="meta-value">💰 {grant['amount']}</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Action buttons row
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    
    with btn_col1:
        if st.button("✍️ Generate Proposal", type="primary", use_container_width=True):
            st.session_state.selected_grant = grant
            st.switch_page("pages/3_✍️_Proposal_Builder.py")
    
    with btn_col2:
        if st.button("📄 Export PDF", use_container_width=True):
            st.info("PDF export feature coming soon!")
    
    with btn_col3:
        if st.button("🔗 Open Grant Website", use_container_width=True):
            st.markdown(f"[Open grant page →]({grant['url']})")
    
    st.markdown("---")
    
    # Tabs for different sections
    tab1, tab2, tab3 = st.tabs([
        "📄 Overview", 
        "✅ Eligibility", 
        "📋 Requirements"
    ])
    
    with tab1:
        st.markdown("### Grant Overview")
        # Use detailed_overview if available, otherwise use description
        overview_text = grant.get('detailed_overview', grant['description'])
        st.markdown(f"""
            <div class="insight-card" style="color: #2d3748;">
                <p>{overview_text}</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### Tags")
        tags_html = " ".join([f'<span style="background-color: #eef6ff; color: #3182ce; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.85rem; margin-right: 0.5rem;">{tag}</span>' for tag in grant['tags']])
        st.markdown(tags_html, unsafe_allow_html=True)
        
    
    with tab2:
        # st.markdown("### Eligibility Checklist")
        # st.markdown("*AI-extracted eligibility criteria with confidence scores*")
        # st.markdown("<br>", unsafe_allow_html=True)
        
        # Use eligibility_checklist from grant data (API format)
        # render_eligibility_checklist(eligibility_checklist)
        st.markdown("### Eligibility Criteria")
        # st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### Source Text")
        st.markdown(f"""
            <div class="insight-card" style="color: #2d3748;">
                <strong>Extracted from grant page:</strong><br>
                "{grant.get('eligibility', 'Eligibility information extracted from the grant webpage.')}"
            </div>
        """, unsafe_allow_html=True)
        
        
    
    with tab3:
        st.markdown("### Application Requirements")
        st.markdown("*Documents and materials needed for your application*")
        
        # Use application_requirements from grant data (API format)
        for i, doc in enumerate(application_requirements, 1):
            st.checkbox(doc, key=f"req_{i}")
        
        st.markdown("### Extracted Requirements Summary")
        st.markdown("""
            <div class="insight-card" style="color: #2d3748;">
                <strong>Application Process:</strong><br>
                1. Submit Letter of Intent by deadline<br>
                2. Receive invitation to submit full proposal<br>
                3. Complete online application form<br>
                4. Upload required documents<br>
                5. Submit project budget and narrative
            </div>
        """, unsafe_allow_html=True)
    
    
    # Sidebar
    with st.sidebar:
        
        st.markdown("### 📊 Quick Stats")
        st.metric("Deadline", grant['deadline'])
        st.metric("Amount", grant['amount'])
        st.metric("Documents Required", len(application_requirements))
        
        st.markdown("---")
        
        st.markdown("### 🔗 Quick Links")
        st.markdown(f"[🌐 Grant Website]({grant['url']})")


if __name__ == "__main__":
    main()
