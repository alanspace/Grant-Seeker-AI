"""
Grant Seeker AI - Main Application Entry Point
A Streamlit multi-page app for finding, analyzing, and writing grant proposals.
"""
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Grant Seeker AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS to hide Streamlit footer and main menu, and style the page
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display: none;}
        
        /* Hero section styling */
        .hero-title {
            text-align: center;
            font-size: 3rem;
            font-weight: 700;
            color: #1a365d;
        }
        
        .hero-subtitle {
            text-align: center;
            font-size: 1.3rem;
            color: #4a5568;
        }
        
        /* Feature card styling */
        .feature-card {
            background-color: #eef6ff;
            border-radius: 12px;
            padding: 2rem;
            margin: 1rem 0;
        }
        
        .feature-item {
            display: flex;
            align-items: center;
            margin: 1rem 0;
            font-size: 1.1rem;
        }
        
        .feature-icon {
            font-size: 1.5rem;
            margin-right: 1rem;
        }
        
        /* CTA button styling */
        .stButton > button {
            width: 100%;
            padding: 0.75rem 2rem;
            font-size: 1.2rem;
            font-weight: 600;
        }
        
        /* Footer styling */
        .custom-footer {
            text-align: center;
            color: #718096;
            font-size: 0.9rem;
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 1px solid #e2e8f0;
        }
        
        /* Card container */
        .card-container {
            background-color: #eef6ff;
            border-radius: 12px;
            padding: 2rem;
            margin: 1.5rem 0;
        }
    </style>
""", unsafe_allow_html=True)


def main():
    """Main function to render the landing page."""
    
    # Add some top padding
    # st.markdown("<br>", unsafe_allow_html=True)
    
    # Hero Section
    st.markdown('<h1 class="hero-title">🚀 Grant Seeker AI</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="hero-subtitle">Your AI assistant for finding, analyzing, and writing grant proposals</p>',
        unsafe_allow_html=True
    )
    
    # Spacer
    # st.markdown("<br>", unsafe_allow_html=True)
    
    # Feature Summary Block
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
            <div class="card-container">
                <h3 style="text-align: center; color: #2d3748; margin-bottom: 1.5rem;">What We Help You Do</h3>
                <div class="feature-item" style="color: #2d3748;>
                    <span class="feature-icon">🔍</span>
                    <span><strong>Find relevant grants</strong> — Search our database or paste grant URLs to discover opportunities</span>
                </div>
                <div class="feature-item" style="color: #2d3748;>
                    <span class="feature-icon">📋</span>
                    <span><strong>Extract eligibility & requirements</strong> — AI analyzes grant pages to pull key details</span>
                </div>
                <div class="feature-item" style="color: #2d3748;>
                    <span class="feature-icon">✍️</span>
                    <span><strong>Generate a professional proposal</strong> — Draft compelling proposals with AI assistance</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Primary CTA Button
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🔎 ✨ Start Searching Grants", type="primary", use_container_width=True):
            st.switch_page("pages/1_🔍_Search_Grants.py")
        
        # Secondary actions
        st.markdown("<br>", unsafe_allow_html=True)
        
        sec_col1, sec_col2 = st.columns(2)
        with sec_col1:
            if st.button("📖 How It Works", use_container_width=True):
                st.info("""
                    **How it works**

                    1. Describe your project and search for matching grants.
                    2. AI extracts eligibility, deadlines, and key requirements from grant pages.
                    3. Generate a tailored proposal draft and refine it interactively.
                """)
        
        with sec_col2:
            if st.button("📄 See Sample", use_container_width=True):
                st.info("""
                    **Sample — Community Garden for Urban Youth**

                    Mission: Empower youth with hands-on gardens teaching STEM, nutrition, and entrepreneurship.

                    AI delivered: top matches, key requirements, and a ready proposal draft. Try it with your project.
                """)
    
    # Footer
    # st.markdown("""
    #     <div class="custom-footer">
    #         Built for Google ADK Capstone • Team Project
    #     </div>
    # """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
