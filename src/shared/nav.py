"""
Navigation bar for the app.
Renders a top navigation bar with buttons for each page.
"""

import streamlit as st

def render_nav():
    """Render the top navigation bar."""
    
    # Initialize session state for current page if not exists
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'
    
    # Define pages
    pages = {
        'home': {'icon': '🏠', 'label': 'Home'},
        'finance': {'icon': '💰', 'label': 'Finance'},
        'food': {'icon': '🍽️', 'label': 'Food'},
        'insights': {'icon': '📊', 'label': 'Insights'},
    }
    
    # Create the nav bar with columns
    cols = st.columns(len(pages))
    
    # Add a button for each page
    for idx, (page_id, page_info) in enumerate(pages.items()):
        with cols[idx]:
            # Style the button based on current page
            is_active = st.session_state.current_page == page_id
            button_label = f"{page_info['icon']} {page_info['label']}"
            
            if st.button(
                button_label,
                key=f"nav_{page_id}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                if not is_active:
                    st.session_state.current_page = page_id
                    st.rerun()
    
    st.divider()