import streamlit as st

def render_header():
    display_rate = st.session_state.get('display_rate', 3.766)
    st.title("💰 Cash Register + Dashboard (PLN / USD)")
    st.caption(f"Exchange rate: 1 USD = {display_rate:.2f} PLN | Data stored in SQLite (persistent)")
