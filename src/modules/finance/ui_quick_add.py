"""
Finance quick add transaction form.
"""
import streamlit as st
from datetime import datetime
from src.modules.finance.data import add_transaction


def render_quick_add():
    """Always-visible compact transaction entry form."""

    st.markdown("""<style>
.quick-add-bar {background:rgba(30,41,59,0.8);border:1px solid #2a3a4b;border-radius:12px;padding:16px 20px;margin-bottom:8px;}
</style>""", unsafe_allow_html=True)

    st.markdown('<div class="quick-add-bar">', unsafe_allow_html=True)

    with st.form(key="quick_add_form", clear_on_submit=True):
        col1, col2, col3, col4 = st.columns([2, 2, 1.2, 1])
        with col1:
            trans_date = st.date_input("Date", datetime.today().date(), label_visibility="collapsed")
        with col2:
            trans_amount = st.number_input(
                "Amount (PLN)", min_value=0.01, step=0.01,
                format="%.2f", placeholder="Amount (PLN)",
                label_visibility="collapsed"
            )
        with col3:
            trans_type = st.selectbox(
                "Type", ["💸 Expense", "💰 Income"],
                label_visibility="collapsed"
            )
        with col4:
            submitted = st.form_submit_button("➕ Add", type="primary", use_container_width=True)

        if submitted:
            if trans_amount <= 0:
                st.error("Amount must be > 0.")
            else:
                is_income = "Income" in trans_type
                add_transaction(
                    trans_date,
                    trans_amount if is_income else 0.0,
                    0.0 if is_income else trans_amount
                )
                st.success(f"✅ {'Income' if is_income else 'Expense'}: {trans_amount:.2f} PLN")
                if 'last_saved' in st.session_state:
                    del st.session_state['last_saved']
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
