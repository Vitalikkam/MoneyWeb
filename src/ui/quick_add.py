import streamlit as st
from datetime import datetime
from src.supabase_client import add_transaction

def render_quick_add():
    if not st.session_state.get('show_quick_add', False):
        return
    
    with st.expander("➕ Quick Add Transaction", expanded=True):
        with st.form(key="quick_add_form", clear_on_submit=True):
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                trans_date = st.date_input("Date", datetime.today().date())
            with col2:
                trans_amount = st.number_input("Amount (PLN)", min_value=0.01, step=0.01, format="%.2f", placeholder="0.00")
            with col3:
                trans_type = st.selectbox("Type", ["Expense", "Income"])
            
            submitted = st.form_submit_button("➕ Add Transaction", type="primary", use_container_width=True)
            if submitted:
                if trans_amount <= 0:
                    st.error("Amount must be greater than 0.")
                else:
                    if trans_type == "Income":
                        deposit = trans_amount
                        withdrawal = 0.0
                    else:
                        deposit = 0.0
                        withdrawal = trans_amount
                    add_transaction(trans_date, deposit, withdrawal)
                    st.success(f"✅ Added {trans_type}: {trans_amount:.2f} PLN on {trans_date.strftime('%Y-%m-%d')}")
                    if 'last_saved' in st.session_state:
                        del st.session_state.last_saved
                    st.rerun()