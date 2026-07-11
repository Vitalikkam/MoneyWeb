"""
Dashboard home page.
"""
import streamlit as st
import pandas as pd
from datetime import datetime


def render_dashboard():
    """Main dashboard page."""
    from src.modules.finance.data import get_all_transactions, get_summary
    from src.modules.food.data import get_daily_summary
    from src.modules.supplements.data import get_supplements
    from src.modules.supplements.config import DEFAULT_SUPPLEMENTS
    from src.modules.vocabulary.data import get_words_due_for_review, get_stats
    from src.modules.food.ui import VITAMIN_GOALS

    rate = st.session_state.get('display_rate', 3.766)
    today = datetime.today().strftime('%Y-%m-%d')

    df_finance   = get_all_transactions()
    food_summary = get_daily_summary()
    vocab_stats  = get_stats()
    due_words    = get_words_due_for_review()

    # Supplements today
    supp_df = get_supplements(today, today)
    supp_taken = len(supp_df[supp_df['taken'] == 1]) if not supp_df.empty else 0
    supp_total = len(DEFAULT_SUPPLEMENTS)

    # Finance summary
    fin_summary = get_summary() if not df_finance.empty else {}
    balance_pln = fin_summary.get('total_balance', 0)
    balance_usd = balance_pln / rate

    # --- Styles ---
    st.markdown("""<style>
.db-card {background:rgba(30,41,59,0.8);border:1px solid #2a3a4b;border-radius:16px;padding:20px 24px;margin-bottom:12px;}
.db-card-title {color:#94a3b8;font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;}
.db-kpi {font-size:32px;font-weight:800;color:#f8fafc;line-height:1.1;}
.db-kpi-sub {font-size:13px;color:#64748b;margin-top:2px;}
.db-tx-row {display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid #1e293b;}
.db-tx-date {color:#64748b;font-size:12px;}
.db-tx-pos {color:#4ade80;font-weight:600;}
.db-tx-neg {color:#f87171;font-weight:600;}
.db-section-header {font-size:13px;font-weight:600;color:#94a3b8;text-transform:uppercase;letter-spacing:1px;margin:4px 0 10px 0;}
</style>""", unsafe_allow_html=True)

    # --- Top KPI strip ---
    k1, k2, k3, k4 = st.columns(4)

    with k1:
        color = "#4ade80" if balance_pln >= 0 else "#f87171"
        st.markdown(
            f'<div class="db-card">'
            f'<div class="db-card-title">💰 Balance</div>'
            f'<div class="db-kpi" style="color:{color}">{balance_pln:,.0f} zł</div>'
            f'<div class="db-kpi-sub">${balance_usd:,.0f} USD</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    with k2:
        cal = food_summary.get('total_calories', 0)
        cal_pct = min(cal / 3000 * 100, 100)
        st.markdown(
            f'<div class="db-card">'
            f'<div class="db-card-title">🔥 Calories Today</div>'
            f'<div class="db-kpi">{cal:.0f}</div>'
            f'<div class="db-kpi-sub">/ 3000 kcal · {cal_pct:.0f}%</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    with k3:
        supp_color = "#4ade80" if supp_taken == supp_total else "#fbbf24" if supp_taken > 0 else "#94a3b8"
        st.markdown(
            f'<div class="db-card">'
            f'<div class="db-card-title">💊 Supplements</div>'
            f'<div class="db-kpi" style="color:{supp_color}">{supp_taken}/{supp_total}</div>'
            f'<div class="db-kpi-sub">taken today</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    with k4:
        due_count = len(due_words)
        due_color = "#f87171" if due_count > 0 else "#4ade80"
        st.markdown(
            f'<div class="db-card">'
            f'<div class="db-card-title">📚 Vocab Due</div>'
            f'<div class="db-kpi" style="color:{due_color}">{due_count}</div>'
            f'<div class="db-kpi-sub">words to review · {vocab_stats["total"]} total</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Main content: Finance | Food + Supplements ---
    col_left, col_right = st.columns([1.1, 0.9])

    # === LEFT: Finance ===
    with col_left:
        st.markdown('<div class="db-section-header">💰 Finance</div>', unsafe_allow_html=True)

        if df_finance.empty:
            st.info("No transactions yet.")
        else:
            # Mini balance chart
            from src.modules.finance.plots import create_river_chart
            df_bal = df_finance.copy()
            df_bal['Deposit']    = pd.to_numeric(df_bal['Deposit'], errors='coerce').fillna(0)
            df_bal['Withdrawal'] = pd.to_numeric(df_bal['Withdrawal'], errors='coerce').fillna(0)
            df_bal['Balance']    = (df_bal['Deposit'] - df_bal['Withdrawal']).cumsum()

            fig = create_river_chart(df_bal)
            if fig:
                fig.update_layout(height=180, margin=dict(l=0, r=0, t=0, b=0),
                                  showlegend=False, yaxis_title="")
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

            # Recent transactions
            st.markdown('<div class="db-section-header" style="margin-top:12px;">Recent Transactions</div>', unsafe_allow_html=True)
            df_recent = df_bal.sort_values('Date', ascending=False).head(5)
            tx_rows = ""
            for _, row in df_recent.iterrows():
                date_str = pd.to_datetime(row['Date']).strftime('%b %d')
                if row['Deposit'] > 0:
                    amt_html = f'<span class="db-tx-pos">+{row["Deposit"]:,.2f} zł</span>'
                else:
                    amt_html = f'<span class="db-tx-neg">-{row["Withdrawal"]:,.2f} zł</span>'
                tx_rows += (
                    f'<div class="db-tx-row">'
                    f'<span class="db-tx-date">{date_str}</span>'
                    f'{amt_html}'
                    f'</div>'
                )
            st.markdown(f'<div class="db-card" style="padding:12px 16px;">{tx_rows}</div>', unsafe_allow_html=True)

    # === RIGHT: Food + Supplements ===
    with col_right:
        # Food macros
        st.markdown('<div class="db-section-header">🍽️ Today\'s Nutrition</div>', unsafe_allow_html=True)
        if food_summary['meal_count'] == 0:
            st.markdown('<div class="db-card"><span style="color:#64748b;">No meals logged today.</span></div>', unsafe_allow_html=True)
        else:
            macros = [
                ("🔥 Calories", food_summary['total_calories'], 3000, "kcal"),
                ("💪 Protein",  food_summary['total_protein'],  155,  "g"),
                ("🍞 Carbs",    food_summary['total_carbs'],    350,  "g"),
                ("🥑 Fat",      food_summary['total_fat'],      80,   "g"),
            ]
            for label, val, goal, unit in macros:
                pct = min(val / goal, 1.0)
                st.progress(pct, text=f"{label}: {val:.0f} / {goal} {unit}  ({pct*100:.0f}%)")

            # Vitamins — only if any logged
            has_vitamins = any(
                food_summary.get(k, 0) > 0 for k in VITAMIN_GOALS
            )
            if has_vitamins:
                with st.expander("🧬 Vitamins & Minerals"):
                    from src.modules.food.ui import render_vitamin_progress
                    render_vitamin_progress(food_summary)

        st.markdown("<br>", unsafe_allow_html=True)

        # Supplements today
        st.markdown('<div class="db-section-header">💊 Supplements Today</div>', unsafe_allow_html=True)
        if supp_df.empty:
            st.markdown('<div class="db-card"><span style="color:#64748b;">No supplement data.</span></div>', unsafe_allow_html=True)
        else:
            taken_names = set(supp_df[supp_df['taken'] == 1]['supplement_name'].tolist())
            rows_html = ""
            for s in DEFAULT_SUPPLEMENTS:
                name = s['name']
                taken = name in taken_names
                icon  = "✅" if taken else "⬜"
                color = "#f8fafc" if taken else "#64748b"
                rows_html += f'<div style="display:flex;align-items:center;gap:8px;padding:4px 0;border-bottom:1px solid #1e293b;"><span>{icon}</span><span style="color:{color};font-size:13px;">{name}</span></div>'
            st.markdown(f'<div class="db-card" style="padding:12px 16px;">{rows_html}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Quick Actions ---
    st.markdown('<div class="db-section-header">⚡ Quick Actions</div>', unsafe_allow_html=True)
    q1, q2, q3, q4, q5 = st.columns(5)
    actions = [
        (q1, "💰 Finance",     'finance'),
        (q2, "🍽️ Log Meal",    'food'),
        (q3, "💊 Supplements", 'supplements'),
        (q4, "📚 Vocabulary",  'vocabulary'),
        (q5, "🔄 Review Words",'vocabulary'),
    ]
    for col, label, page in actions:
        with col:
            if st.button(label, use_container_width=True, key=f"dash_{label}"):
                st.session_state.current_page = page
                st.rerun()
