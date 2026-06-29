import streamlit as st
import pandas as pd
from src.supabase_client import get_all_transactions, save_dataframe
from src.config import COLORS
from src.currency import convert_pln_to_usd

def add_balance_column(df):
    df = df.copy()
    df['Deposit'] = pd.to_numeric(df['Deposit'], errors='coerce').fillna(0)
    df['Withdrawal'] = pd.to_numeric(df['Withdrawal'], errors='coerce').fillna(0)
    df['Balance'] = (df['Deposit'] - df['Withdrawal']).cumsum()
    return df

def get_data_with_balance():
    df = get_all_transactions()
    return None if df.empty else add_balance_column(df)

def render_kpi(df_with_balance):
    total_dep = df_with_balance['Deposit'].sum()
    total_with = df_with_balance['Withdrawal'].sum()
    current_bal = df_with_balance['Balance'].iloc[-1] if not df_with_balance.empty else 0
    delta = df_with_balance['Balance'].iloc[-1] - df_with_balance['Balance'].iloc[-2] if len(df_with_balance) > 1 else 0
    
    rate = st.session_state.get('display_rate', 3.766)
    dep_usd = convert_pln_to_usd(total_dep, rate)
    with_usd = convert_pln_to_usd(total_with, rate)
    bal_usd = convert_pln_to_usd(current_bal, rate)
    delta_usd = convert_pln_to_usd(delta, rate)
    
    st.subheader("📊 Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("📥 Deposits (PLN)", f"{total_dep:,.2f} zł")
    col2.metric("📤 Withdrawals (PLN)", f"{total_with:,.2f} zł")
    col3.metric("💰 Balance (PLN)", f"{current_bal:,.2f} zł", delta=f"{delta:,.2f} zł")
    
    st.caption("Equivalent in USD")
    col1u, col2u, col3u = st.columns(3)
    col1u.metric("Deposits (USD)", f"${dep_usd:,.2f}" if dep_usd is not None else "N/A")
    col2u.metric("Withdrawals (USD)", f"${with_usd:,.2f}" if with_usd is not None else "N/A")
    col3u.metric("Balance (USD)", f"${bal_usd:,.2f}" if bal_usd is not None else "N/A", delta=f"${delta_usd:,.2f}" if delta_usd is not None else "N/A")
    st.divider()

def render_table():
    df = get_all_transactions()
    if df.empty:
        st.info("💾 No transactions yet. Add one or import CSV.")
        return
    
    df_with_balance = add_balance_column(df)
    
    st.subheader("📋 Transaction Register (PLN)")
    editable_cols = ['Date', 'Deposit', 'Withdrawal']
    edited_df = st.data_editor(
        df[editable_cols],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Date": st.column_config.DateColumn("Date", format="MMM DD, YYYY"),
            "Deposit": st.column_config.NumberColumn("Deposit (+ PLN)", format="%.2f", min_value=0),
            "Withdrawal": st.column_config.NumberColumn("Withdrawal (- PLN)", format="%.2f", min_value=0)
        },
        num_rows="dynamic"
    )
    
    edited_df['Date'] = pd.to_datetime(edited_df['Date']).dt.date
    if 'last_saved' not in st.session_state:
        st.session_state.last_saved = df[editable_cols].copy()
    
    if not edited_df.equals(st.session_state.last_saved):
        save_dataframe(edited_df)
        st.session_state.last_saved = edited_df.copy()
        st.rerun()
    
    df_with_balance = add_balance_column(get_all_transactions())
    
    st.caption("⬇️ Full Register with Running Balance (PLN)")
    
    def color_balance(val):
        if isinstance(val, (int, float)):
            if val > 0: return f'color: {COLORS["green"]}; font-weight: 700;'
            elif val < 0: return f'color: {COLORS["red"]}; font-weight: 700;'
            else: return f'color: {COLORS["text_muted"]};'
        return ''
    
    def color_deposit(val):
        return f'color: {COLORS["green"]}; font-weight: 600;' if isinstance(val, (int, float)) and val > 0 else ''
    
    def color_withdrawal(val):
        return f'color: {COLORS["red"]}; font-weight: 600;' if isinstance(val, (int, float)) and val > 0 else ''
    
    styled_df = (df_with_balance.style
        .applymap(color_balance, subset=['Balance'])
        .applymap(color_deposit, subset=['Deposit'])
        .applymap(color_withdrawal, subset=['Withdrawal']))
    
    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Date": st.column_config.DateColumn("Date", format="MMM DD, YYYY"),
            "Deposit": st.column_config.NumberColumn("Deposit (+)", format="%.2f"),
            "Withdrawal": st.column_config.NumberColumn("Withdrawal (-)", format="%.2f"),
            "Balance": st.column_config.NumberColumn("💰 Balance", format="%.2f")
        }
    )
    
    render_kpi(df_with_balance)
