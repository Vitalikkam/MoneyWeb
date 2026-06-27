import streamlit as st
from src.plots import create_river_chart, create_net_chart, prepare_grouped_data
from src.data_manager import get_all_transactions
from .table import add_balance_column

def render_charts(df=None):
    if df is None:
        raw = get_all_transactions()
        if raw.empty:
            st.info("No transactions yet.")
            return
        df = add_balance_column(raw)
    
    st.subheader("📈 Visual Analytics")
    
    rate = st.session_state.get('display_rate', 3.766)
    
    st.caption("💰 Balance over Time - PLN")
    fig_river_pln = create_river_chart(df)
    if fig_river_pln:
        st.plotly_chart(fig_river_pln, use_container_width=True, config={'displayModeBar': False})
    
    st.caption("💵 Balance over Time - USD")
    df_usd = df.copy()
    df_usd['Balance'] = df_usd['Balance'] / rate
    fig_river_usd = create_river_chart(df_usd, currency='$')
    if fig_river_usd:
        st.plotly_chart(fig_river_usd, use_container_width=True, config={'displayModeBar': False})
    
    st.caption("📊 Net Change (Deposits - Withdrawals) - PLN")
    tab1, tab2, tab3 = st.tabs(["📅 Daily", "📆 Weekly", "📊 Monthly"])
    
    for tab, period in zip([tab1, tab2, tab3], ['Daily', 'Weekly', 'Monthly']):
        data = prepare_grouped_data(df, period)
        fig = create_net_chart(data)
        if fig:
            tab.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        else:
            tab.info(f"No {period.lower()} data")
