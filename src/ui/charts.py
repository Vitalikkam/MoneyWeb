import streamlit as st
from src.plots import create_river_chart, create_net_chart, prepare_grouped_data
from src.supabase_client import get_all_transactions
from .table import add_balance_column

def render_charts(df=None):
    if df is None:
        df = get_all_transactions()
        if df.empty:
            st.info("No transactions yet.")
            return
        df_with_balance = add_balance_column(df)
    else:
        df_with_balance = df
    
    st.subheader("📈 Visual Analytics")
    
    st.caption("💰 Your Money River (Balance over Time) - PLN")
    fig_river = create_river_chart(df_with_balance)
    if fig_river:
        st.plotly_chart(fig_river, use_container_width=True, config={'displayModeBar': False})
    
    st.caption("📊 Net Change (Deposits - Withdrawals) - PLN")
    tab1, tab2, tab3 = st.tabs(["📅 Daily", "📆 Weekly", "📊 Monthly"])
    
    daily_data = prepare_grouped_data(df_with_balance, 'Daily')
    fig_daily = create_net_chart(daily_data)
    if fig_daily:
        tab1.plotly_chart(fig_daily, use_container_width=True, config={'displayModeBar': False})
    else:
        tab1.info("No daily data")
    
    weekly_data = prepare_grouped_data(df_with_balance, 'Weekly')
    fig_weekly = create_net_chart(weekly_data)
    if fig_weekly:
        tab2.plotly_chart(fig_weekly, use_container_width=True, config={'displayModeBar': False})
    else:
        tab2.info("No weekly data")
    
    monthly_data = prepare_grouped_data(df_with_balance, 'Monthly')
    fig_monthly = create_net_chart(monthly_data)
    if fig_monthly:
        tab3.plotly_chart(fig_monthly, use_container_width=True, config={'displayModeBar': False})
    else:
        tab3.info("No monthly data")