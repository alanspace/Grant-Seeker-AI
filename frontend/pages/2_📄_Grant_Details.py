import streamlit as st
import json

st.title("📄 Grant Details")

# Check if a grant is selected
if 'selected_grant' not in st.session_state or not st.session_state.selected_grant:
    st.warning("No grant selected. Please go back to search.")
    if st.button("🔙 Go to Search"):
        st.switch_page("pages/1_🔍_Search_Grants.py")
    st.stop()

details = st.session_state.selected_grant

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
    <p style="margin: 10px 0 0 0; font-size: 16px; color: #555;">{details.get('description', '')}</p>
    <div style="margin-top: 15px;">
        <span style="background: #e0e7ff; color: #4338ca; padding: 4px 12px; border-radius: 20px; font-size: 14px; font-weight: 500; margin-right: 10px;">
            💰 {details['amount']}
        </span>
        <span style="background: #ecfdf5; color: #047857; padding: 4px 12px; border-radius: 20px; font-size: 14px; font-weight: 500;">
            📅 Deadline: {details['deadline']}
        </span>
    </div>
</div>
""", unsafe_allow_html=True)


# ---------------------- ELIGIBILITY SECTION ----------------------
st.markdown("""
### 🟦 Eligibility Requirements
These conditions must be met to qualify for this grant:
""")

st.markdown("<div style='margin-left: 15px; font-size:16px;'>", unsafe_allow_html=True)
for item in details.get("eligibility", []):
    st.markdown(f"✔️ {item}")
st.markdown("</div>", unsafe_allow_html=True)


# ---------------------- DOCUMENT REQUIREMENTS ----------------------
st.markdown("""
### 🟧 Required Documents
Prepare the following information to complete the application:
""")

st.markdown("<div style='margin-left: 15px; font-size:16px;'>", unsafe_allow_html=True)
for item in details.get("requirements", []):
    st.markdown(f"📄 {item}")
st.markdown("</div>", unsafe_allow_html=True)


# ---------------------- CTA BUTTON ----------------------
st.write("")
st.markdown("""
<div style="text-align:center; margin-top: 25px;">
""", unsafe_allow_html=True)

if st.button("✍️ Generate Proposal", type="primary"):
    st.switch_page("pages/3_✍️_Draft_Proposal.py")

st.markdown("</div>", unsafe_allow_html=True)
