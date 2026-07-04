import streamlit as st
from .config import COLORS

def apply_dark_theme():
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        * {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }}

        .stApp {{ background-color: {COLORS['bg_primary']}; }}
        .block-container {{ padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1400px; }}

        section[data-testid="stSidebar"] {{
            background-color: #0f172a !important;
            border-right: 1px solid #1e293b;
        }}

        h1, h2, h3, h4, h5 {{ font-weight: 600 !important; letter-spacing: -0.01em; color: #ffffff !important; }}
        h1 {{ font-size: 2.2rem !important; margin-bottom: 0.25rem !important; }}
        h2 {{ font-size: 1.5rem !important; margin-top: 0.5rem !important; }}

        div[data-testid="metric-container"] {{
            background: linear-gradient(145deg, #1e293b, #172032);
            border: 1px solid #2a3a4b;
            border-radius: 12px;
            padding: 0.75rem 1rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.4);
            transition: all 0.2s ease;
        }}
        div[data-testid="metric-container"]:hover {{
            border-color: #4ade80;
            transform: translateY(-2px);
            box-shadow: 0 6px 18px rgba(0,0,0,0.5);
        }}
        div[data-testid="metric-container"] label {{
            color: {COLORS['text_muted']} !important;
            font-weight: 500; font-size: 0.85rem;
            text-transform: uppercase; letter-spacing: 0.03em;
        }}
        div[data-testid="metric-container"] div[data-testid="metric-value"] {{
            color: #ffffff !important; font-weight: 700; font-size: 1.8rem; margin-top: 0.2rem;
        }}
        div[data-testid="metric-container"] div[data-testid="metric-delta"] {{
            font-weight: 500; font-size: 0.9rem;
        }}

        .stDataFrame, .stDataFrame tbody, .stDataFrame td,
        .stDataEditor, .stDataEditor tbody, .stDataEditor td,
        .stDataFrame thead th, .stDataEditor thead th {{
            background-color: #1e293b !important;
            color: {COLORS['text_primary']} !important;
            border-color: #2a3a4b !important;
            font-size: 0.9rem !important;
        }}
        .stDataFrame thead th, .stDataEditor thead th {{
            background-color: #0f172a !important;
            color: #94a3b8 !important; font-weight: 600 !important;
            text-transform: uppercase; font-size: 0.75rem !important;
            letter-spacing: 0.05em; border-bottom: 2px solid #2a3a4b !important;
        }}
        .stDataFrame tbody tr:hover td, .stDataEditor tbody tr:hover td {{
            background-color: #2a3a4b !important;
        }}

        .stTextInput input, .stNumberInput input, .stDateInput input {{
            background-color: #1e293b !important; border: 1px solid #2a3a4b !important;
            border-radius: 8px !important; color: {COLORS['text_primary']} !important;
            padding: 0.5rem 0.75rem !important; transition: border-color 0.2s;
        }}
        .stTextInput input:focus, .stNumberInput input:focus, .stDateInput input:focus {{
            border-color: #4ade80 !important; outline: none;
        }}

        .stButton button {{
            border-radius: 8px !important; font-weight: 600 !important;
            padding: 0.5rem 1rem !important; transition: all 0.2s ease !important; border: none !important;
        }}
        .stButton button[kind="primary"] {{
            background: linear-gradient(135deg, #4ade80, #22d3ee) !important;
            color: #0f172a !important; box-shadow: 0 4px 12px rgba(74, 222, 128, 0.3);
        }}
        .stButton button[kind="primary"]:hover {{
            transform: scale(1.02); box-shadow: 0 6px 20px rgba(74, 222, 128, 0.4);
        }}
        .stButton button[kind="secondary"] {{
            background-color: #2a3a4b !important; color: {COLORS['text_secondary']} !important;
        }}
        .stButton button[kind="secondary"]:hover {{ background-color: #3a4b5b !important; }}

        .streamlit-expanderHeader {{
            background-color: #1e293b !important; border: 1px solid #2a3a4b !important;
            border-radius: 10px !important; color: {COLORS['text_primary']} !important;
            font-weight: 500; padding: 0.75rem 1rem !important;
        }}
        .streamlit-expanderHeader:hover {{ border-color: #4ade80; }}

        .stTabs [data-baseweb="tab-list"] {{
            background-color: #1e293b; border-radius: 10px; padding: 0.25rem; gap: 0.25rem;
        }}
        .stTabs [data-baseweb="tab"] {{
            color: {COLORS['text_muted']} !important; border-radius: 6px !important;
            padding: 0.4rem 1rem !important; font-weight: 500;
        }}
        .stTabs [aria-selected="true"] {{ background-color: #0f172a !important; color: #ffffff !important; }}

        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}

        ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
        ::-webkit-scrollbar-track {{ background: #0f172a; }}
        ::-webkit-scrollbar-thumb {{ background: #2a3a4b; border-radius: 10px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: #4ade80; }}

        .stCaption {{ color: {COLORS['text_muted']} !important; font-size: 0.8rem !important; }}
        .stPlotlyChart {{
            background: #1e293b; border-radius: 12px; padding: 0.5rem;
            border: 1px solid #2a3a4b; box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }}
    </style>
    """, unsafe_allow_html=True)
