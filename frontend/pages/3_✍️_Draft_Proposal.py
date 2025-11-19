import streamlit as st
import json

st.title("✍️ Draft Proposal")

# Load proposal text
with open("dummy_data/proposal.json") as f:
    proposal = json.load(f)["proposal"]


# --------- HEADER BLOCK ---------
st.markdown("""
<div style="
    background: #fff4db;
    padding: 20px;
    border-radius: 12px;
    border-left: 6px solid #ffb347;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
    margin-bottom: 25px;
">
<h3 style="margin:0;">AI-Generated Grant Proposal</h3>
<p style="color:#555;">Review, edit, and save your proposal before submission.</p>
</div>
""", unsafe_allow_html=True)


# --------- PROPOSAL DISPLAY ---------
st.markdown("""
<div style="font-size:16px; margin-bottom:10px;">
<b>Your Proposal:</b>
</div>
""", unsafe_allow_html=True)

proposal_text = st.text_area(
    "",
    proposal,
    height=350,
)

# --------- BUTTONS BLOCK ---------
col1, col2, col3 = st.columns([1,2,1])
with col2:
    colA, colB = st.columns(2)

    with colA:
        copy_btn = st.button("📋 Copy to Clipboard")

    with colB:
        download_btn = st.download_button(
            label="📄 Download Proposal",
            file_name="proposal.txt",
            mime="text/plain",
            data=proposal_text
        )

# Fully working clipboard copy
if copy_btn:
    st.markdown(f"""
        <script>
        navigator.clipboard.writeText(`{proposal_text}`);
        </script>
    """, unsafe_allow_html=True)
    st.success("Copied!")
