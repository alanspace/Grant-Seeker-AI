import streamlit as st

def grant_card(grant):
    st.markdown(f"""
    <div style="
        padding: 18px;
        margin-bottom: 15px;
        border-radius: 12px;
        background: #f8faff;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.06);
        border: 1px solid #e8eef8;
    ">
        <h3 style="margin: 0; font-size: 22px;">{grant['title']}</h3>
        <p style="margin: 5px 0 10px 0; font-size: 16px;">
            <b>Amount:</b> {grant['amount']} <br>
            <b>Deadline:</b> {grant['deadline']}
        </p>
    </div>
    """, unsafe_allow_html=True)
