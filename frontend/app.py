import streamlit as st

st.set_page_config(
    page_title="Grant Seeker’s Co-Pilot",
    page_icon="🚀",
    layout="wide"
)

st.markdown("""
<style>
footer {visibility: hidden;}
#MainMenu {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ------ Hero Section ------
st.markdown("""
    <div style="text-align: center; padding-top: 40px; padding-bottom: 10px;">
        <h1 style="font-size: 48px; margin-bottom: 10px;">🚀 Grant Seeker’s Co-Pilot</h1>
        <h3 style="color: #555;">Your AI assistant for finding, analyzing, and writing grant proposals</h3>
    </div>
""", unsafe_allow_html=True)

st.write("")
st.write("")

# ------- Feature Section --------
st.markdown("""
<div style="
    background: #eef6ff;
    padding: 25px;
    border-radius: 12px;
    width: 70%;
    margin: auto;
    box-shadow: 0 0 10px rgba(0,0,0,0.05);
">
    <h4>✨ What this tool helps you do:</h4>
    <ul style="font-size: 18px;">
        <li>Find relevant grants</li>
        <li>Extract eligibility & requirements</li>
        <li>Automatically generate a professional proposal</li>
    </ul>
</div>
""", unsafe_allow_html=True)

st.write("")
st.write("")

# ------ CTA Button ------
st.markdown("""
<div style="text-align: center; margin-top: 5px; margin-bottom: 5px;">
""", unsafe_allow_html=True)

st.page_link(
    "pages/1_🔍_Search_Grants.py",
    label="🔎 ✨ Start Searching Grants"
)

# Reduce bottom empty space
st.write("")
st.write("")

# Footer
st.markdown("""
<br><br><hr>
<p style="text-align:center; color:#888; font-size:14px;">
Built for Google ADK Capstone • Team Project
</p>
""", unsafe_allow_html=True)

