import streamlit as st
from src.modules.finance.plots import create_river_chart, create_net_chart, prepare_grouped_data, create_projected_river_chart
from src.modules.finance.data import get_all_transactions
from .ui_table import add_balance_column

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

    # ── Projected balance ───────────────────────────────────────────────────
    rate = st.session_state.get('display_rate', 3.766)
    col_label, col_slider = st.columns([2, 1])
    with col_label:
        st.caption("🔮 Projected Balance (USD) — based on completed months")
    with col_slider:
        days_ahead = st.select_slider(
            "Horizon",
            options=[30, 60, 90, 180],
            value=90,
            label_visibility="collapsed",
            key="proj_horizon"
        )
    fig_proj = create_projected_river_chart(df_with_balance, days_ahead=days_ahead, rate=rate)
    if fig_proj:
        st.plotly_chart(fig_proj, use_container_width=True, config={'displayModeBar': False})
    else:
        st.info("Not enough completed months to project balance.")

    st.caption("📊 Net Change (Deposits - Withdrawals) - PLN")
    tab1, tab2, tab3 = st.tabs(["📅 Daily", "📆 Weekly", "📊 Monthly"])

    with tab1:
        daily_data = prepare_grouped_data(df_with_balance, 'Daily')
        fig_daily = create_net_chart(daily_data)
        if fig_daily:
            st.plotly_chart(fig_daily, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("No daily data")

    with tab2:
        weekly_data = prepare_grouped_data(df_with_balance, 'Weekly')
        fig_weekly = create_net_chart(weekly_data)
        if fig_weekly:
            st.plotly_chart(fig_weekly, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("No weekly data")

    with tab3:
        monthly_data = prepare_grouped_data(df_with_balance, 'Monthly')
        fig_monthly = create_net_chart(monthly_data)
        if fig_monthly:
            st.plotly_chart(fig_monthly, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("No monthly data")