import streamlit as st

# --- MUST BE FIRST ---
st.set_page_config(
    page_title="💰 Life Dashboard",
    layout="wide"
)

# --- Now everything else ---
from src.shared.nav import render_nav
from src.modules.finance.data import get_all_transactions, add_transaction, save_dataframe, delete_transaction, get_summary, clear_all_data
from src.shared.styles import apply_dark_theme
from src.modules.finance.ui_header import render_header
from src.modules.finance.ui_quick_add import render_quick_add
from src.modules.finance.ui_table import render_table, render_kpi, get_data_with_balance
from src.modules.finance.ui_charts import render_charts
from src.shared.currency import get_current_rate
import pandas as pd

apply_dark_theme()

# --- CSS to control sidebar visibility ---
st.markdown("""
<style>
    /* Hide sidebar by default on all pages */
    section[data-testid="stSidebar"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Render Navigation ---
render_nav()

# --- Get Current Page ---
current_page = st.session_state.get('current_page', 'home')

# --- Render Content Based on Current Page ---
if current_page == 'home':
    from src.modules.dashboard.ui import render_dashboard
    render_dashboard()

elif current_page == 'finance':
    render_header()
    render_quick_add()

    # Load data
    df = get_all_transactions()

    if df.empty:
        st.info("💾 No transactions yet. Add one or import CSV.")
        st.stop()

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


elif current_page == 'supplements':
    # --- Supplements Page ---
    from src.modules.supplements.ui import render_supplement_tracker
    render_supplement_tracker()

elif current_page == 'vocabulary':
    from src.modules.vocabulary.ui import render_vocabulary_tracker
    render_vocabulary_tracker()

elif current_page == 'learning':
    from src.modules.learning.ui import render_learning_tracker
    render_learning_tracker()


