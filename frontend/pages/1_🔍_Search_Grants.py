import streamlit as st
import json
from utils.ui_components import grant_card

st.title("🔍 Search Grants")
st.write("Describe your project idea and we’ll find relevant grants for you.")

project_text = st.text_area(
    "Your Project Description:",
    placeholder="Write about your project, target audience, purpose, impact..."
)

# Loading placeholder
results_container = st.container()

if st.button("Search Grants"):
    with st.spinner("🔎 Finding the best matching grants..."):
        with open("dummy_data/grants.json") as f:
            grants = json.load(f)

    with results_container:
        st.subheader("🎯 Matching Grants")
        st.write("")

        if not grants:
            st.warning("No grants found. Try refining your project description.")
        else:
            for g in grants:
                grant_card(g)
                st.page_link(
                    "pages/2_📄_Grant_Details.py",
                    label="📄 View Grant Details",
                )
                st.write("---")
