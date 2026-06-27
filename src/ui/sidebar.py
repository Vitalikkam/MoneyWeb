import streamlit as st
import pandas as pd
from datetime import datetime
from src.currency import get_current_rate
from src.data_manager import append_csv_data, export_to_csv, clear_all_data

def render_sidebar():
    with st.sidebar:
        st.header("💱 Currency Settings")
        
        current_rate = get_current_rate()
        if current_rate is not None:
            st.metric("Live USD/PLN Rate", f"{current_rate:.4f}")
            default_manual_value = current_rate
        else:
            st.error("❌ Failed to fetch live exchange rate. Please use manual override.")
            default_manual_value = 3.766
        
        use_manual = st.checkbox("Override rate manually", value=(current_rate is None))
        if use_manual:
            manual_rate = st.number_input(
                "1 USD = ? PLN",
                min_value=1.0, max_value=10.0,
                value=float(default_manual_value),
                step=0.001, format="%.3f"
            )
            st.session_state['display_rate'] = manual_rate
        else:
            st.session_state['display_rate'] = current_rate if current_rate is not None else 3.766
        
        if st.button("🔄 Refresh Exchange Rate"):
            if 'rate_fetched_at' in st.session_state:
                del st.session_state.rate_fetched_at
            st.rerun()
        
        st.divider()
        
        st.subheader("📤 Import CSV")
        with st.form(key="csv_import_form"):
            uploaded_file = st.file_uploader(
                "Choose a CSV file", type=['csv'], key="csv_uploader",
                help="CSV must have columns: Date, Deposit, Withdrawal (or Date, Amount with sign)"
            )
            submit_import = st.form_submit_button("📥 Import CSV")
        
        if submit_import and uploaded_file is not None:
            success, message, count = append_csv_data(uploaded_file)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
        
        csv_data = export_to_csv()
        if csv_data:
            st.download_button(
                label="📥 Download CSV Export",
                data=csv_data,
                file_name=f"finances_export_{datetime.today().strftime('%Y%m%d')}.csv",
                mime="text/csv", type="primary"
            )
        else:
            st.info("No data to export")
        
        st.divider()
        
        st.subheader("🎛️ UI Options")
        st.checkbox("Show Quick Add Form", value=False, key="show_quick_add")
        st.checkbox("Show Transaction Table", value=False, key="show_table")
        
        st.divider()
        
        st.subheader("🗄️ Database Actions")
        if st.button("🗑️ Clear All Data", type="secondary"):
            clear_all_data()
            st.session_state.last_saved = pd.DataFrame()
            st.rerun()
