import streamlit as st


def logout_section(redirect_page="Home.py"):
    """
    Render a reusable logout button inside the sidebar. The button clears the
    login-related session state and redirects the user back to the login page.
    """
    if not st.session_state.get("logged_in"):
        return

    if st.button("Log out"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.info("Logged out successfully.")
        st.switch_page(redirect_page)
        st.stop()
