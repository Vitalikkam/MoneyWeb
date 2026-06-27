import streamlit as st
from src.styles import apply_dark_theme
from src.data_manager import init_db
from src.ui.sidebar import render_sidebar
from src.ui.header import render_header
from src.ui.quick_add import render_quick_add
from src.ui.table import render_table, render_kpi, get_data_with_balance
from src.ui.charts import render_charts

st.set_page_config(page_title="💰 Cash Register", layout="wide")
apply_dark_theme()
init_db()

render_sidebar()
render_header()
render_quick_add()

df_balance = get_data_with_balance()
if df_balance is None:
    st.info("💾 No transactions yet. Add one or import CSV.")
    st.stop()

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

st.caption("💡 Use the Quick Add form or import CSV. Toggle UI elements in the sidebar.")
