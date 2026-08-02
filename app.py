import os
import sys

# FORCE production environment
os.environ["APP_ENV"] = "prod"

# Debug
print(f"APP_ENV set to: {os.environ.get('APP_ENV')}")

import streamlit as st

# --- MUST BE FIRST ---
st.set_page_config(
    page_title="💰 Life Dashboard",
    layout="wide"
)

# --- Now everything else ---
from src.shared.nav import render_nav
from src.shared.styles import apply_dark_theme
from src.modules.finance.ui_header import render_header
from src.modules.finance.ui_quick_add import render_quick_add
from src.modules.finance.ui_table import render_table, render_kpi
from src.modules.finance.ui_charts import render_charts
from src.modules.finance.data import get_all_transactions
from src.modules.dashboard.ui import render_dashboard
import pandas as pd

apply_dark_theme()

# --- Render Navigation ---
render_nav()

# --- Get Current Page ---
current_page = st.session_state.get('current_page', 'home')

# --- Render Content Based on Current Page ---
if current_page == 'home':
    # --- Home Page (Dashboard) ---
    render_dashboard()

elif current_page == 'finance':
    # --- Finance Page ---
    render_header()
    render_quick_add()
    
    # Load data from Supabase
    df = get_all_transactions()
    
    # Check if data exists
    if df.empty:
        st.info("💾 No transactions yet. Add one or import CSV.")
        st.stop()
    
    # Get data with balance
    def add_balance_column(df):
        df = df.copy()
        df['Deposit'] = pd.to_numeric(df['Deposit'], errors='coerce').fillna(0)
        df['Withdrawal'] = pd.to_numeric(df['Withdrawal'], errors='coerce').fillna(0)
        df['Balance'] = (df['Deposit'] - df['Withdrawal']).cumsum()
        return df
    
    df_balance = add_balance_column(df)
    
    show_table = st.session_state.get('show_table', False)
    
    if show_table:
        col_table, col_charts = st.columns([0.4, 0.6])
        with col_table:
            render_table()
        with col_charts:
            render_charts(df_balance)
    else:
        render_kpi(df_balance)
        render_charts(df_balance)

elif current_page == 'food':
    # --- Food Page (Removed) ---
    st.title("🍽️ Food Tracker")
    st.caption("This module has been removed.")
    st.info("The Food Tracker is no longer available. Please use other modules.")

elif current_page == 'supplements':
    # --- Supplements Page ---
    from src.modules.supplements.ui import render_supplement_tracker
    render_supplement_tracker()

elif current_page == 'vocabulary':
    # --- Vocabulary Page ---
    from src.modules.vocabulary.ui import render_vocabulary_tracker
    render_vocabulary_tracker()

elif current_page == 'learning':
    # --- Learning Page ---
    from src.modules.learning.ui import render_learning_tracker
    render_learning_tracker()

elif current_page == 'exercises':
    # --- Exercises Page ---
    from src.modules.exercises.ui import render_exercise_tracker
    render_exercise_tracker()

elif current_page == 'insights':
    # --- Insights Page (Coming Soon) ---
    st.title("📊 Insights")
    st.caption("Cross-module insights and analytics – coming soon!")
    st.info("🚧 This feature is under development.")

st.caption("💡 Use the top navigation to switch between modules.")