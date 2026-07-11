"""
Navigation bar for the app.
Renders a top navigation bar with buttons for each page.
"""

import streamlit as st

def render_nav():
    """Render the top navigation bar."""

    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'

    pages = {
        'home':        {'icon': '🏠', 'label': 'Home'},
        'finance':     {'icon': '💰', 'label': 'Finance'},
        'food':        {'icon': '🍽️', 'label': 'Food'},
        'supplements': {'icon': '💊', 'label': 'Supplements'},
        'vocabulary':  {'icon': '📚', 'label': 'Vocabulary'},
    }

    # Inject nav CSS — active page gets accent underline + brighter text
    st.markdown("""<style>
div[data-testid="stHorizontalBlock"] button[kind="primary"] {
    background: transparent !important;
    border: none !important;
    border-bottom: 3px solid #4ade80 !important;
    border-radius: 0 !important;
    color: #4ade80 !important;
    font-weight: 700 !important;
    box-shadow: none !important;
}
div[data-testid="stHorizontalBlock"] button[kind="secondary"] {
    background: transparent !important;
    border: none !important;
    border-bottom: 3px solid transparent !important;
    border-radius: 0 !important;
    color: #94a3b8 !important;
    font-weight: 500 !important;
    box-shadow: none !important;
}
div[data-testid="stHorizontalBlock"] button[kind="secondary"]:hover {
    color: #f8fafc !important;
    border-bottom-color: #334155 !important;
}
</style>""", unsafe_allow_html=True)

    cols = st.columns(len(pages))
    for idx, (page_id, page_info) in enumerate(pages.items()):
        with cols[idx]:
            is_active = st.session_state.current_page == page_id
            if st.button(
                f"{page_info['icon']} {page_info['label']}",
                key=f"nav_{page_id}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                if not is_active:
                    st.session_state.current_page = page_id
                    st.rerun()

    st.divider()