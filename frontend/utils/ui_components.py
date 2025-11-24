import streamlit as st

def grant_card(grant):
    # Define CSS to make the button look like a card
    # We use a specific class or just target the button within a container if possible,
    # but for simplicity, we'll inject global styles for buttons that match this pattern or rely on the button's key/label structure if needed.
    # However, to avoid affecting ALL buttons, we can't easily scope CSS in Streamlit without a container.
    # A workaround is to style 'div.stButton > button' but that affects all.
    # We will try to make the button content distinctive or just style all buttons in the results area if we can.
    # Actually, let's just style the button generally to be card-like if it has multi-line text.
    
    card_style = """
    <style>
    div.stButton > button {
        width: 100%;
        text-align: left;
        height: auto;
        padding: 20px;
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
        display: block;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 12px rgba(0,0,0,0.1);
        border-color: #4a72ff;
        color: inherit;
    }
    div.stButton > button:focus, div.stButton > button:active {
        background-color: #ffffff !important;
        color: inherit !important;
        border-color: #4a72ff !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
    }
    div.stButton > button p {
        font-size: 16px;
    }
    </style>
    """
    st.markdown(card_style, unsafe_allow_html=True)
    
    # Prepare button label with info
    # Note: Streamlit buttons treat newlines as breaks.
    # We can't use rich HTML inside the button label, so we use text formatting.
    label = f"{grant['title']}\n💰 {grant['amount']}  |  📅 Deadline: {grant['deadline']}"
    
    # Render the button
    # We return the button's clicked state
    return st.button(label, key=f"grant_btn_{grant['id']}")
