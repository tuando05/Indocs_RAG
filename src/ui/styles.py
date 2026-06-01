import streamlit as st

def inject_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    [data-testid="stSidebar"] {
        background-color: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }

    .stButton>button {
        border-radius: 6px;
    }

    .source-card {
        background-color: rgba(59, 130, 246, 0.05);
        border-left: 3px solid #3b82f6;
        padding: 8px 12px;
        margin: 5px 0;
        border-radius: 4px;
        font-size: 0.9em;
    }
    </style>
    """, unsafe_allow_html=True)
