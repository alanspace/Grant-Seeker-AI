import streamlit as st
import json
import time

st.title("✍️ Draft Proposal")

# Initialize session state for proposal
if 'generated_proposal' not in st.session_state:
    st.session_state.generated_proposal = ""

# Header
st.markdown("""
<div style="
    background: #fff4db;
    padding: 20px;
    border-radius: 12px;
    border-left: 6px solid #ffb347;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
    margin-bottom: 25px;
">
<h3 style="margin:0; color: #d97706;">AI-Generated Grant Proposal</h3>
<p style="color:#555; margin-top: 5px;">Review, edit, and save your proposal before submission.</p>
</div>
""", unsafe_allow_html=True)

# Generate Button
if st.button("✨ Generate Proposal", type="primary"):
    with st.spinner('AI agents are researching and writing...'):
        # Simulate generation time
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.02)
            progress_bar.progress(i + 1)
        
        # Load sample proposal
        try:
            with open("sample_data/proposal.json", "r", encoding="utf-8") as f:
                st.session_state.generated_proposal = json.load(f)["proposal"]
        except Exception as e:
            st.error(f"Error loading proposal: {e}")
        
        # Clear progress bar
        progress_bar.empty()

# Display Proposal if it exists
if st.session_state.generated_proposal:
    st.markdown("### 📝 Your Proposal Draft")
    
    proposal_text = st.text_area(
        "Edit your proposal:",
        value=st.session_state.generated_proposal,
        height=400,
        help="You can edit the text directly here."
    )
    
    # Update session state if user edits
    st.session_state.generated_proposal = proposal_text

    # Action Buttons
    st.write("")
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("📋 Copy to Clipboard"):
            st.markdown(f"""
                <script>
                navigator.clipboard.writeText(`{proposal_text}`);
                </script>
            """, unsafe_allow_html=True)
            st.toast("Copied to clipboard!", icon="✅")

    with col2:
        st.download_button(
            label="💾 Download",
            data=proposal_text,
            file_name="grant_proposal.txt",
            mime="text/plain"
        )
else:
    st.info("Click 'Generate Proposal' to start the drafting process.")

