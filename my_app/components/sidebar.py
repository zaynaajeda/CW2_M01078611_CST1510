import streamlit as st

def logout_section(redirect_page="Home.py"):
    """
    Implement a logout button inside sidebar which 
    clears all session states and redirect user to login page
    """
    if not st.session_state.get("logged_in"):
        return

    #Verify if button is clicked
    if st.button("Log out"):
        #Reset session state variables
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.session_state.selected_domain = None
        st.session_state.analyst_domain = ""
        st.info("Logged out successfully.")
        st.switch_page(redirect_page)
        st.stop()
