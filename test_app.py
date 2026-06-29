import streamlit as st

st.set_page_config(
    page_title="Sidebar Test",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Main Content")

with st.sidebar:
    st.header("🔵 SIDEBAR TEST")
    st.write("If you see this, the sidebar works!")
    st.button("Click me")
