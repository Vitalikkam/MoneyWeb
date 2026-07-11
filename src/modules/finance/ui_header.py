"""
Finance page header — rate badge, table toggle, CSV import/export.
"""
import streamlit as st
from datetime import datetime
from src.shared.currency import get_current_rate, fetch_exchange_rate
from src.modules.finance.csv_utils import append_csv_data, export_to_csv


def render_header():
    """Top bar: title, live rate, table toggle, CSV tools."""

    # Ensure rate is in session state
    if 'display_rate' not in st.session_state:
        rate = get_current_rate()
        st.session_state['display_rate'] = rate if rate else 3.766

    rate = st.session_state['display_rate']

    # --- Top row ---
    col_title, col_rate, col_toggle, col_csv = st.columns([3, 2, 1, 1])

    with col_title:
        st.markdown("## 💰 Finance")

    with col_rate:
        st.markdown(f"""<div style='background:rgba(74,222,128,0.1);border:1px solid rgba(74,222,128,0.3);
            border-radius:10px;padding:6px 14px;display:inline-flex;align-items:center;gap:10px;'>
            <span style='color:#4ade80;font-weight:700;font-size:15px;'>1 USD = {rate:.3f} PLN</span>
        </div>""", unsafe_allow_html=True)

    with col_toggle:
        show_table = st.session_state.get('show_table', False)
        if st.button("📋 Table" if not show_table else "📋 Hide", use_container_width=True):
            st.session_state['show_table'] = not show_table
            st.rerun()

    with col_csv:
        with st.popover("📤 CSV", use_container_width=True):
            _render_csv_tools()
            st.divider()
            _render_rate_settings(rate)

    st.divider()


def _render_csv_tools():
    """CSV import and export controls."""
    st.markdown("**Import CSV**")
    uploaded = st.file_uploader(
        "CSV file (Date, Deposit, Withdrawal)",
        type=['csv'],
        key="csv_uploader",
        label_visibility="collapsed"
    )
    if st.button("📥 Import", type="primary", use_container_width=True, key="csv_import_btn"):
        if uploaded:
            success, message, count = append_csv_data(uploaded)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
        else:
            st.warning("Select a CSV file first.")

    st.markdown("**Export CSV**")
    csv_data = export_to_csv()
    if csv_data:
        st.download_button(
            label="⬇️ Download Export",
            data=csv_data,
            file_name=f"finances_{datetime.today().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.caption("No data to export.")


def _render_rate_settings(current_rate):
    """Currency rate override controls."""
    st.markdown("**Exchange Rate**")
    use_manual = st.checkbox("Override manually", value=False, key="rate_manual_override")
    if use_manual:
        manual = st.number_input(
            "1 USD = ? PLN",
            min_value=1.0, max_value=10.0,
            value=float(current_rate),
            step=0.001, format="%.3f",
            key="manual_rate_input"
        )
        st.session_state['display_rate'] = manual
    else:
        if st.button("🔄 Refresh Rate", use_container_width=True, key="refresh_rate_btn"):
            fresh = fetch_exchange_rate()
            if fresh:
                st.session_state['display_rate'] = fresh
                st.success(f"Updated: {fresh:.4f}")
                st.rerun()
            else:
                st.error("Failed to fetch rate.")
