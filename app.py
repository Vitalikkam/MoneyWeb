import streamlit as st
from src.supabase_client import get_all_transactions, add_transaction, save_dataframe, delete_transaction, get_summary
from src.styles import apply_dark_theme
from src.ui.sidebar import render_sidebar
from src.ui.header import render_header
from src.ui.quick_add import render_quick_add
from src.ui.table import render_table, render_kpi, get_data_with_balance
from src.ui.charts import render_charts
import pandas as pd

st.set_page_config(
    page_title="💰 Cash Register",
    layout="wide",
    initial_sidebar_state="expanded"
)
apply_dark_theme()

render_sidebar()

st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {
            display: block !important;
            visibility: visible !important;
            opacity: 1 !important;
            width: 300px !important;
            min-width: 300px !important;
            transform: none !important;
        }
    </style>
    <script>
    (function() {
        const showSidebar = () => {
            const sidebar = document.querySelector('section[data-testid="stSidebar"]');
            const button = document.querySelector(
                'button[aria-label*="sidebar"], button[title*="sidebar"], button[data-testid*="sidebar"]'
            );
            if (sidebar) {
                sidebar.style.display = 'block';
                sidebar.style.visibility = 'visible';
                sidebar.style.opacity = '1';
                sidebar.style.width = '300px';
                sidebar.style.minWidth = '300px';
                sidebar.style.transform = 'none';
            }
            const hidden = sidebar && (sidebar.offsetWidth === 0 || window.getComputedStyle(sidebar).visibility === 'hidden');
            if (button && hidden) {
                button.click();
            }
        };
        let attempts = 0;
        const interval = setInterval(() => {
            showSidebar();
            attempts += 1;
            if (attempts > 12) clearInterval(interval);
        }, 250);
        setTimeout(() => clearInterval(interval), 3500);
    })();
    </script>
    """,
    unsafe_allow_html=True,
)

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

st.caption("💡 Use the Quick Add form. Data is stored in Supabase cloud.")