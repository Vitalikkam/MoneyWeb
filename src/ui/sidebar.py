import streamlit as st
import pandas as pd
from datetime import datetime
from src.currency import get_current_rate, fetch_exchange_rate
from src.supabase_client import append_csv_data, export_to_csv, clear_all_data
import logging

# Capture logs for display
log_messages = []

class StreamlitLogHandler(logging.Handler):
    def emit(self, record):
        log_messages.append(self.format(record))

# Set up logging to capture messages
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = StreamlitLogHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S'))
logger.addHandler(handler)

def render_sidebar():
    with st.sidebar:
        st.header("💱 Currency Settings")
        
        # Show exchange rate with status
        current_rate = get_current_rate()
        if current_rate is not None:
            st.metric("Live USD/PLN Rate", f"{current_rate:.4f}")
            st.caption("✅ Rate fetched successfully")
            default_manual_value = current_rate
        else:
            st.error("❌ Failed to fetch live exchange rate.")
            st.caption("💡 Using manual override or fallback")
            default_manual_value = 3.766
        
        use_manual = st.checkbox("Override rate manually", value=(current_rate is None))
        if use_manual:
            manual_rate = st.number_input(
                "1 USD = ? PLN",
                min_value=1.0,
                max_value=10.0,
                value=float(default_manual_value),
                step=0.001,
                format="%.3f"
            )
            st.session_state['display_rate'] = manual_rate
        else:
            st.session_state['display_rate'] = current_rate if current_rate is not None else 3.766
        
        # Refresh button with debug info
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("🔄 Refresh Exchange Rate", use_container_width=True):
                if 'rate_fetched_at' in st.session_state:
                    del st.session_state.rate_fetched_at
                # Force fresh fetch
                fresh_rate = fetch_exchange_rate()
                if fresh_rate:
                    st.session_state.exchange_rate = fresh_rate
                    st.session_state.rate_fetched_at = datetime.now()
                    st.success(f"✅ Rate updated: {fresh_rate:.4f}")
                else:
                    st.error("❌ Failed to fetch rate")
                st.rerun()
        with col2:
            if st.button("📋 Log", use_container_width=True):
                st.session_state.show_log = not st.session_state.get('show_log', False)
        
        # Show debug log if enabled
        if st.session_state.get('show_log', False):
            st.divider()
            st.caption("🔍 Debug Log")
            log_text = "\n".join(log_messages[-10:]) if log_messages else "No logs yet"
            st.code(log_text, language="text")
        
        st.divider()
        
        # CSV Import
        st.subheader("📤 Import CSV")
        with st.form(key="csv_import_form"):
            uploaded_file = st.file_uploader(
                "Choose a CSV file",
                type=['csv'],
                key="csv_uploader",
                help="CSV must have columns: Date, Deposit, Withdrawal"
            )
            submit_import = st.form_submit_button("📥 Import CSV")
        
        if submit_import and uploaded_file is not None:
            success, message, count = append_csv_data(uploaded_file)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
        
        # CSV Export
        csv_data = export_to_csv()
        if csv_data:
            st.download_button(
                label="📥 Download CSV Export",
                data=csv_data,
                file_name=f"finances_export_{datetime.today().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                type="primary"
            )
        else:
            st.info("No data to export")
        
        st.divider()
        
        # UI Toggles
        st.subheader("🎛️ UI Options")
        st.checkbox("Show Quick Add Form", value=False, key="show_quick_add")
        st.checkbox("Show Transaction Table", value=False, key="show_table")
        
        st.divider()
        
        # Database Actions
        st.subheader("🗄️ Database Actions")
        if st.button("🗑️ Clear All Data", type="secondary"):
            if clear_all_data():
                st.success("All data cleared!")
                st.rerun()
            else:
                st.error("Failed to clear data.")