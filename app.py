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
from src.modules.finance.ui_sidebar import render_sidebar
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
    # --- Home Page (Dashboard) ---
    st.title("🏠 Dashboard")
    st.caption("Welcome to your Life Dashboard! Overview of all your data.")
    
    # Get exchange rate
    rate = st.session_state.get('display_rate', 3.766)
    
    # --- Finance Summary ---
    df_finance = get_all_transactions()
    
    # --- Food Summary ---
    from src.modules.food.data import get_daily_summary
    food_summary = get_daily_summary()
    
    # --- Dashboard Layout ---
    col1, col2 = st.columns(2)
    
    # === FINANCE COLUMN ===
    with col1:
        st.subheader("💰 Finance")
        if df_finance.empty:
            st.info("No transactions yet.")
        else:
            summary = get_summary()
            
            # PLN values
            total_balance_pln = summary['total_balance']
            total_deposits_pln = summary['total_deposits']
            total_withdrawals_pln = summary['total_withdrawals']
            
            # USD values
            total_balance_usd = total_balance_pln / rate
            total_deposits_usd = total_deposits_pln / rate
            total_withdrawals_usd = total_withdrawals_pln / rate
            
            # Finance metrics
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("💰 Balance", f"{total_balance_pln:,.2f} zł", f"${total_balance_usd:,.2f} USD")
            col_b.metric("📥 Deposits", f"{total_deposits_pln:,.2f} zł")
            col_c.metric("📤 Withdrawals", f"{total_withdrawals_pln:,.2f} zł")
            
            # Recent transactions table
            st.caption("📋 Recent Transactions")
            
            # Show last 5 transactions
            df_recent = df_finance.tail(5).sort_values('Date', ascending=False)
            if not df_recent.empty:
                for _, row in df_recent.iterrows():
                    if row['Deposit'] > 0:
                        amount = f"+{row['Deposit']:.2f} zł"
                        color = "🟢"
                    else:
                        amount = f"-{row['Withdrawal']:.2f} zł"
                        color = "🔴"
                    
                    # Format date
                    date_str = pd.to_datetime(row['Date']).strftime('%b %d')
                    
                    # Show transaction
                    st.write(f"{date_str}  {color}  {amount}")
            else:
                st.caption("No recent transactions")
            
            # Mini chart
            st.caption("Net Worth Trend")
            from src.modules.finance.plots import create_river_chart
            df_balance = df_finance.copy()
            df_balance['Deposit'] = pd.to_numeric(df_balance['Deposit'], errors='coerce').fillna(0)
            df_balance['Withdrawal'] = pd.to_numeric(df_balance['Withdrawal'], errors='coerce').fillna(0)
            df_balance['Balance'] = (df_balance['Deposit'] - df_balance['Withdrawal']).cumsum()
            
            fig = create_river_chart(df_balance)
            if fig:
                fig.update_layout(height=200, yaxis_title="PLN", showlegend=False)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    # === FOOD COLUMN ===
    with col2:
        st.subheader("🍽️ Food")
        if food_summary['meal_count'] == 0:
            st.info("No meals logged today. Log your first meal!")
        else:
            # --- Daily Goals ---
            st.caption("🎯 Daily Progress")
            
            # Calories
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.progress(
                    min(food_summary['total_calories'] / 3000, 1.0),
                    text=f"🔥 {food_summary['total_calories']:.0f} / 3000 kcal"
                )
            with col_b:
                st.caption(f"{min(food_summary['total_calories'] / 3000 * 100, 100):.0f}%")
            
            # Protein
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.progress(
                    min(food_summary['total_protein'] / 155, 1.0),
                    text=f"💪 {food_summary['total_protein']:.1f} / 155 g"
                )
            with col_b:
                st.caption(f"{min(food_summary['total_protein'] / 155 * 100, 100):.0f}%")
            
            # Carbs
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.progress(
                    min(food_summary['total_carbs'] / 350, 1.0),
                    text=f"🍞 {food_summary['total_carbs']:.1f} / 350 g"
                )
            with col_b:
                st.caption(f"{min(food_summary['total_carbs'] / 350 * 100, 100):.0f}%")
            
            # Fat
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.progress(
                    min(food_summary['total_fat'] / 80, 1.0),
                    text=f"🥑 {food_summary['total_fat']:.1f} / 80 g"
                )
            with col_b:
                st.caption(f"{min(food_summary['total_fat'] / 80 * 100, 100):.0f}%")
            
            # --- Vitamins & Minerals Progress Bars ---
            st.caption("🧬 Vitamins & Minerals")
            
            # Vitamin A
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.progress(
                    min(food_summary.get('total_vitamin_a', 0) / 900, 1.0),
                    text=f"🅰️ Vitamin A: {food_summary.get('total_vitamin_a', 0):.0f} / 900 µg"
                )
            with col_b:
                st.caption(f"{min(food_summary.get('total_vitamin_a', 0) / 900 * 100, 100):.0f}%")
            
            # Vitamin C
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.progress(
                    min(food_summary.get('total_vitamin_c', 0) / 200, 1.0),
                    text=f"🅲 Vitamin C: {food_summary.get('total_vitamin_c', 0):.0f} / 200 mg"
                )
            with col_b:
                st.caption(f"{min(food_summary.get('total_vitamin_c', 0) / 200 * 100, 100):.0f}%")
            
            # Vitamin D
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.progress(
                    min(food_summary.get('total_vitamin_d', 0) / 75, 1.0),
                    text=f"🅳 Vitamin D: {food_summary.get('total_vitamin_d', 0):.0f} / 75 µg"
                )
            with col_b:
                st.caption(f"{min(food_summary.get('total_vitamin_d', 0) / 75 * 100, 100):.0f}%")
            
            # Calcium
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.progress(
                    min(food_summary.get('total_calcium', 0) / 1100, 1.0),
                    text=f"🧂 Calcium: {food_summary.get('total_calcium', 0):.0f} / 1100 mg"
                )
            with col_b:
                st.caption(f"{min(food_summary.get('total_calcium', 0) / 1100 * 100, 100):.0f}%")
            
            # Iron
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.progress(
                    min(food_summary.get('total_iron', 0) / 9, 1.0),
                    text=f"🔩 Iron: {food_summary.get('total_iron', 0):.1f} / 9 mg"
                )
            with col_b:
                st.caption(f"{min(food_summary.get('total_iron', 0) / 9 * 100, 100):.0f}%")
            
            # Magnesium
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.progress(
                    min(food_summary.get('total_magnesium', 0) / 400, 1.0),
                    text=f"🧲 Magnesium: {food_summary.get('total_magnesium', 0):.0f} / 400 mg"
                )
            with col_b:
                st.caption(f"{min(food_summary.get('total_magnesium', 0) / 400 * 100, 100):.0f}%")
            
            # Zinc
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.progress(
                    min(food_summary.get('total_zinc', 0) / 13, 1.0),
                    text=f"🔋 Zinc: {food_summary.get('total_zinc', 0):.1f} / 13 mg"
                )
            with col_b:
                st.caption(f"{min(food_summary.get('total_zinc', 0) / 13 * 100, 100):.0f}%")
            
            # Potassium
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.progress(
                    min(food_summary.get('total_potassium', 0) / 4000, 1.0),
                    text=f"🍌 Potassium: {food_summary.get('total_potassium', 0):.0f} / 4000 mg"
                )
            with col_b:
                st.caption(f"{min(food_summary.get('total_potassium', 0) / 4000 * 100, 100):.0f}%")
    
    st.divider()
    
    # === Quick Actions ===
    st.subheader("⚡ Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("💰 Add Transaction", use_container_width=True):
            st.session_state.current_page = 'finance'
            st.rerun()
    
    with col2:
        if st.button("🍽️ Log Meal", use_container_width=True):
            st.session_state.current_page = 'food'
            st.rerun()
    
    with col3:
        if st.button("📊 View Finance", use_container_width=True):
            st.session_state.current_page = 'finance'
            st.rerun()
    
    with col4:
        if st.button("📈 View Insights", use_container_width=True):
            st.session_state.current_page = 'insights'
            st.rerun()

elif current_page == 'finance':
    # --- Show sidebar on Finance page ---
    st.markdown("""
    <style>
        section[data-testid="stSidebar"] {
            display: block !important;
            width: 300px !important;
            min-width: 300px !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    render_sidebar()
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

elif current_page == 'food':
    # --- Food Page ---
    from src.modules.food.ui import render_food_tracker
    render_food_tracker()

elif current_page == 'insights':
    # --- Insights Page (Coming Soon) ---
    st.title("📊 Insights")
    st.caption("Cross-module insights and analytics – coming soon!")
    st.info("🚧 This feature is under development.")

st.caption("💡 Use the sidebar for Finance settings and CSV tools.")