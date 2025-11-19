import streamlit as st
import json

st.title("📄 Grant Details")

# Load the selected grant details
with open("dummy_data/grant_details.json") as f:
    details = json.load(f)


# ---------------------- HEADER CARD ----------------------
st.markdown(f"""
<div style="
    background: linear-gradient(135deg, #eef3ff 0%, #f8fbff 100%);
    padding: 25px;
    border-radius: 14px;
    border-left: 6px solid #4a72ff;
    margin-bottom: 30px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
">
    <h2 style="margin: 0; font-weight: 700; color:#2a2f3b;">{details['title']}</h2>
</div>
""", unsafe_allow_html=True)


# ---------------------- ELIGIBILITY SECTION ----------------------
st.markdown("""
### 🟦 Eligibility Requirements
These conditions must be met to qualify for this grant:
""")

st.markdown("<div style='margin-left: 15px; font-size:16px;'>", unsafe_allow_html=True)
for item in details["eligibility"]:
    st.markdown(f"✔️ {item}")
st.markdown("</div>", unsafe_allow_html=True)


# ---------------------- DOCUMENT REQUIREMENTS ----------------------
st.markdown("""
### 🟧 Required Documents
Prepare the following information to complete the application:
""")

st.markdown("<div style='margin-left: 15px; font-size:16px;'>", unsafe_allow_html=True)
for item in details["requirements"]:
    st.markdown(f"📄 {item}")
st.markdown("</div>", unsafe_allow_html=True)


# ---------------------- CTA BUTTON ----------------------
st.write("")
st.markdown("""
<div style="text-align:center; margin-top: 25px;">
""", unsafe_allow_html=True)

st.page_link(
    "pages/3_✍️_Draft_Proposal.py",
    label="✍️ Generate Proposal",
)

st.markdown("</div>", unsafe_allow_html=True)
