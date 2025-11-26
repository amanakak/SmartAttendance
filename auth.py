import streamlit as st



USERS = {
    "teacher": "pass123",
    "admin": "admin123"
}

def check_password():
    """Returns `True` if the user had a correct password."""

    # 1. Initialize session state variable
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    # 2. If already logged in, show the sidebar logout button and return True
    if st.session_state["logged_in"]:
        if st.sidebar.button("🔒 Logout"):
            st.session_state["logged_in"] = False
            st.rerun()
        return True

    # 3. If NOT logged in, show the login form
    st.title("🔒 Restricted Access")
    st.write("Please log in to access the Attendance System.")

    username = st.text_input("Teacher ID")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in USERS and USERS[username] == password:
            st.session_state["logged_in"] = True
            st.success("Logged in successfully!")
            st.rerun() # Reload the app to show the actual content
        else:
            st.error("❌ Incorrect ID or Password")

    return False