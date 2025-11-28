import streamlit as st

st.set_page_config(
    page_title="Grant Seeker AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Dark Theme and Layout
st.markdown("""
<style>
    /* Dark Theme Background */
    .stApp {
        background-color: #0e1117;
        color: white;
    }
    
    /* Hide default header/footer */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Center text */
    .centered-text {
        text-align: center;
    }
    
    /* Main Title */
    .main-title {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
    }
    
    /* Subtitle */
    .subtitle {
        font-size: 1.1rem;
        color: #8b92a5;
        margin-bottom: 3rem;
    }
    
    /* Card Container */
    .card-container {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 40px;
        color: #1e293b;
        max-width: 800px;
        margin: 0 auto 40px auto;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
    }
    
    .card-title {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 20px;
        text-align: center;
        color: #0f172a;
    }
    
    .feature-text {
        font-size: 1.15rem;
        line-height: 1.8;
        color: #334155;
        margin-bottom: 15px;
    }
    
    .feature-text strong {
        color: #0f172a;
        font-weight: 600;
    }

    /* Custom Button Styling */
    div.stButton > button[kind="primary"] {
        background-color: #f43f5e; /* Vibrant red/pink */
        color: white;
        border: none;
        padding: 0.8rem 2rem;
        font-size: 1.2rem;
        font-weight: 600;
        border-radius: 8px;
        width: 100%;
        transition: all 0.2s ease-in-out;
        box-shadow: 0 4px 6px rgba(244, 63, 94, 0.3);
    }
    
    div.stButton > button[kind="primary"]:hover {
        background-color: #e11d48;
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(244, 63, 94, 0.4);
    }
    
    div.stButton > button[kind="secondary"] {
        background-color: #1e293b !important;
        color: #e2e8f0 !important;
        border: 1px solid #334155 !important;
    }
    
    div.stButton > button[kind="secondary"]:hover {
        background-color: #334155 !important;
        color: white !important;
        border-color: #475569 !important;
    }

</style>
""", unsafe_allow_html=True)

# --- Main Content ---

# Title Section
st.markdown("""
<div class="centered-text">
<div class="main-title">
<span>🚀</span> Grant Seeker AI
</div>
<div class="subtitle">
Your AI assistant for finding, analyzing, and writing grant proposals
</div>
</div>
""", unsafe_allow_html=True)

# Central Card
st.markdown("""
<div class="card-container">
<div class="card-title">What We Help You Do</div>
<p class="feature-text">
🔍 <strong>Find relevant grants</strong> — Search our database or paste grant URLs to discover opportunities
</p>
<p class="feature-text">
📋 <strong>Extract eligibility & requirements</strong> — AI analyzes grant pages to pull key details
</p>
<p class="feature-text">
✍️ <strong>Generate a professional proposal</strong> — Draft compelling proposals with AI assistance
</p>
</div>
""", unsafe_allow_html=True)

# Action Buttons
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # Primary Call to Action
    if st.button("🔍 ✨ Start Searching Grants", type="primary", use_container_width=True):
        st.switch_page("pages/1_🔍_Search_Grants.py")
    
    st.write("") # Spacer
    
    # Secondary Buttons
    sub_col1, sub_col2 = st.columns(2)
    with sub_col1:
        st.button("📖 How It Works", use_container_width=True)
    with sub_col2:
        st.button("📄 See Sample", use_container_width=True)
