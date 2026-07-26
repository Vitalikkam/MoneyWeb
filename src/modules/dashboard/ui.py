"""
Dashboard UI components – Home page widgets.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from src.modules.finance.data import get_all_transactions, get_summary
from src.modules.supplements.data import get_daily_summary
from src.modules.vocabulary.data import get_stats
from src.modules.learning.data import get_study_streak, get_subjects
from src.shared.currency import get_current_rate

def render_dashboard():
    """Render the main dashboard."""
    st.title("🏠 Dashboard")
    st.caption("Welcome to your Life Dashboard! Overview of all your data.")
    
    # Get exchange rate
    rate = st.session_state.get('display_rate', 3.766)
    
    # --- Layout ---
    col1, col2 = st.columns(2)
    
    # === FINANCE COLUMN ===
    with col1:
        render_finance_widget(rate)
    
    # === SECOND COLUMN (Supplements + Vocabulary + Learning) ===
    with col2:
        render_supplements_widget()
        st.divider()
        render_vocabulary_widget()
        st.divider()
        render_learning_widget()
    
    st.divider()
    
    # === Quick Actions ===
    render_quick_actions()

def render_finance_widget(rate):
    """Render the finance summary widget."""
    st.subheader("💰 Finance")
    
    df = get_all_transactions()
    if df.empty:
        st.info("No transactions yet.")
        return
    
    summary = get_summary()
    
    # PLN values
    total_balance_pln = summary['total_balance']
    total_deposits_pln = summary['total_deposits']
    total_withdrawals_pln = summary['total_withdrawals']
    
    # USD values
    total_balance_usd = total_balance_pln / rate if rate else 0
    total_deposits_usd = total_deposits_pln / rate if rate else 0
    total_withdrawals_usd = total_withdrawals_pln / rate if rate else 0
    
    # Finance metrics
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("💰 Balance", f"{total_balance_pln:,.2f} zł", f"${total_balance_usd:,.2f} USD")
    col_b.metric("📥 Deposits", f"{total_deposits_pln:,.2f} zł")
    col_c.metric("📤 Withdrawals", f"{total_withdrawals_pln:,.2f} zł")
    
    # Recent transactions
    st.caption("📋 Recent Transactions")
    df_recent = df.tail(5).sort_values('Date', ascending=False)
    if not df_recent.empty:
        for _, row in df_recent.iterrows():
            if row['Deposit'] > 0:
                amount = f"+{row['Deposit']:.2f} zł"
                color = "🟢"
            else:
                amount = f"-{row['Withdrawal']:.2f} zł"
                color = "🔴"
            date_str = pd.to_datetime(row['Date']).strftime('%b %d')
            st.write(f"{date_str}  {color}  {amount}")
    else:
        st.caption("No recent transactions")
    
    # Mini chart
    st.caption("Net Worth Trend")
    from src.modules.finance.plots import create_river_chart
    df_balance = df.copy()
    df_balance['Deposit'] = pd.to_numeric(df_balance['Deposit'], errors='coerce').fillna(0)
    df_balance['Withdrawal'] = pd.to_numeric(df_balance['Withdrawal'], errors='coerce').fillna(0)
    df_balance['Balance'] = (df_balance['Deposit'] - df_balance['Withdrawal']).cumsum()
    
    fig = create_river_chart(df_balance)
    if fig:
        fig.update_layout(height=200, yaxis_title="PLN", showlegend=False)
        st.plotly_chart(fig, config={'displayModeBar': False})

def render_supplements_widget():
    """Render the supplements summary widget."""
    st.subheader("💊 Supplements")
    
    today = datetime.today().strftime('%Y-%m-%d')
    summary = get_daily_summary(today)
    
    if summary['total'] > 0:
        pct = summary['percentage']
        st.progress(pct / 100, text=f"{summary['taken']}/{summary['total']} taken ({pct:.0f}%)")
        
        missing = [e for e in summary['entries'] if e.get('taken') == 0]
        if missing:
            st.caption("⚠️ Missing today:")
            for m in missing[:5]:
                st.write(f"• {m['supplement_name']}")
            if len(missing) > 5:
                st.caption(f"... and {len(missing) - 5} more")
        else:
            st.success("✅ All supplements taken today!")
    else:
        st.info("No supplements logged today.")
        if st.button("📋 Go to Supplements", use_container_width=True, key="go_supplements"):
            st.session_state.current_page = 'supplements'
            st.rerun()

def render_vocabulary_widget():
    """Render the vocabulary summary widget."""
    st.subheader("📚 Vocabulary")
    
    stats = get_stats()
    
    if stats['total'] > 0:
        col_a, col_b = st.columns(2)
        col_a.metric("📚 Words", stats['total'])
        col_b.metric("🔄 Due for Review", stats['due'])
        
        if stats['by_level']:
            st.caption("📊 Words by Level")
            level_data = pd.DataFrame({
                'Level': list(stats['by_level'].keys()),
                'Count': list(stats['by_level'].values())
            })
            st.bar_chart(level_data.set_index('Level'))
        
        if st.button("📚 Go to Vocabulary", use_container_width=True, key="go_vocabulary"):
            st.session_state.current_page = 'vocabulary'
            st.rerun()
    else:
        st.info("No words in your vocabulary yet.")
        if st.button("📚 Go to Vocabulary", use_container_width=True, key="go_vocabulary_empty"):
            st.session_state.current_page = 'vocabulary'
            st.rerun()

def render_learning_widget():
    """Render the learning summary widget."""
    st.subheader("🎓 Learning")
    
    subjects = get_subjects()
    total = len(subjects) if not subjects.empty else 0
    active = len(subjects[subjects['status'] == 'In Progress']) if not subjects.empty else 0
    streak = get_study_streak()
    
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("📚 Subjects", total)
    col_b.metric("🔄 Active", active)
    col_c.metric("🔥 Streak", f"{streak} days")
    
    if total > 0:
        if st.button("🎓 Go to Learning", use_container_width=True, key="go_learning"):
            st.session_state.current_page = 'learning'
            st.rerun()
    else:
        st.caption("No subjects yet. Start tracking your learning!")

def render_quick_actions():
    """Render quick action buttons."""
    st.subheader("⚡ Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("💰 Add Transaction", use_container_width=True):
            st.session_state.current_page = 'finance'
            st.rerun()
    
    with col2:
        if st.button("📊 View Finance", use_container_width=True):
            st.session_state.current_page = 'finance'
            st.rerun()
    
    with col3:
        if st.button("📚 Vocabulary", use_container_width=True):
            st.session_state.current_page = 'vocabulary'
            st.rerun()
    
    with col4:
        if st.button("🎓 Learning", use_container_width=True):
            st.session_state.current_page = 'learning'
            st.rerun()