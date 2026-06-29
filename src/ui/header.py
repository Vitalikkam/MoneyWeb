import streamlit as st

def render_header():
    display_rate = st.session_state.get('display_rate', 3.766)
    st.title("💰 Cash Register + Dashboard (PLN / USD)")
    st.caption(f"Exchange rate: 1 USD = {display_rate:.2f} PLN | Data stored in SQLite (persistent)")

    if st.button("🔧 Reset sidebar view"):
        st.session_state.sidebar_reset_requested = True

    if st.session_state.get('sidebar_reset_requested', False):
        st.markdown(
            """
            <script>
            (function() {
                const tryOpenSidebar = () => {
                    const button = document.querySelector(
                        'button[aria-label*="sidebar"], button[title*="sidebar"], button[data-testid*="sidebar"]'
                    );
                    if (button) {
                        button.click();
                        return true;
                    }
                    const sidebar = document.querySelector('section[data-testid="stSidebar"]');
                    if (sidebar) {
                        sidebar.style.display = 'block';
                        sidebar.style.visibility = 'visible';
                        sidebar.style.width = '300px';
                        sidebar.style.minWidth = '300px';
                        return true;
                    }
                    return false;
                };
                const interval = setInterval(() => {
                    if (tryOpenSidebar()) {
                        clearInterval(interval);
                    }
                }, 500);
            })();
            </script>
            """,
            unsafe_allow_html=True,
        )
        st.session_state.sidebar_reset_requested = False
