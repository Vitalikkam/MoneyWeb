import streamlit as st
from src.supabase_client import get_all_transactions, add_transaction, save_dataframe, delete_transaction, get_summary
from src.styles import apply_dark_theme
from src.ui.sidebar import render_sidebar
from src.ui.header import render_header
from src.ui.quick_add import render_quick_add
from src.ui.table import render_table, render_kpi, get_data_with_balance
from src.ui.charts import render_charts
import pandas as pd

st.set_page_config(page_title="💰 Cash Register", layout="wide")
apply_dark_theme()

render_sidebar()
render_header()
render_quick_add()

# Load data from Supabase
df = get_all_transactions()

# Check if data exists
if df.empty:
    st.info("💾 No transactions yet. Add one or import CSV.")
    st.stop()

# Get data with balance (for compatibility with existing UI)
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
        # Note: render_table() currently uses data_manager. We'll update it separately.
        render_table()
    with col_charts:
        render_charts(df_balance)
else:
    render_kpi(df_balance)
    render_charts(df_balance)

st.caption("💡 Use the Quick Add form. Data is stored in Supabase cloud.")