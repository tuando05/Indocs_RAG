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

    /* Accordion nguồn trích dẫn nâng cao */
    details.source-details {
        background: var(--background-color);
        border: 1px solid var(--secondary-background-color);
        border-radius: 8px;
        margin: 8px 0;
        padding: 8px 14px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        transition: border-color 0.2s, box-shadow 0.2s;
    }
    
    details.source-details:hover {
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border-color: var(--primary-color);
    }
    
    details.source-details[open] {
        border-color: var(--primary-color);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.08);
    }
    
    summary.source-summary {
        display: flex;
        align-items: center;
        cursor: pointer;
        font-weight: 500;
        outline: none;
        user-select: none;
        gap: 6px;
    }
    
    summary.source-summary::-webkit-details-marker {
        display: none;
    }
    
    summary.source-summary::after {
        content: "▼";
        font-size: 0.75rem;
        margin-left: auto;
        transition: transform 0.2s;
        color: var(--primary-color);
    }
    
    details.source-details[open] summary.source-summary::after {
        transform: rotate(180deg);
    }
    
    .source-icon {
        font-size: 1.1em;
    }
    
    .source-name {
        font-size: 0.9rem;
        color: var(--text-color);
        font-weight: 600;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        max-width: 75%;
    }
    
    .source-badge {
        background-color: rgba(59, 130, 246, 0.1);
        color: #3b82f6;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        white-space: nowrap;
    }
    
    .source-body {
        margin-top: 8px;
        padding-top: 8px;
        border-top: 1px solid var(--secondary-background-color);
        font-size: 0.85rem;
        color: var(--text-color);
        opacity: 0.85;
        line-height: 1.5;
        font-style: italic;
        white-space: pre-wrap;
        max-height: 200px;
        overflow-y: auto;
    }
    </style>
    """, unsafe_allow_html=True)
