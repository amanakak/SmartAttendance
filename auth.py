import streamlit as st
import os
import base64

# --- CREDENTIALS ---
USERS = {
    "teacher": "pass123",
    "admin": "admin123"
}

def set_background():
    """
    Finds 'background.jpg' in the main folder and sets it as the app background.
    """
    # Get the path to the image relative to this file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    bg_image_path = os.path.join(current_dir, "background.jpg")

    if os.path.exists(bg_image_path):
        with open(bg_image_path, "rb") as f:
            data = f.read()
        
        # Convert image to Base64 string
        bin_str = base64.b64encode(data).decode()
        
        # Inject CSS
        page_bg_img = f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{bin_str}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        
        /* Make the main content background semi-transparent white so text is readable */
        .block-container {{
            background-color: rgba(255, 255, 255, 0.85);
            padding: 2rem;
            border-radius: 10px;
            margin-top: 2rem;
        }}
        </style>
        """
        st.markdown(page_bg_img, unsafe_allow_html=True)

def check_password():
    """Returns `True` if the user had a correct password."""
    
    # 1. APPLY BACKGROUND IMMEDIATELY
    set_background()

    # 2. Initialize session state variable
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    # 3. If already logged in, show the sidebar logout button and return True
    if st.session_state["logged_in"]:
        if st.sidebar.button("🔒 Logout"):
            st.session_state["logged_in"] = False
            st.rerun()
        return True

    # 4. If NOT logged in, show the login form
    st.title("🔒 Restricted Access")
    st.write("Please log in to access the Attendance System.")

    username = st.text_input("Teacher ID")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in USERS and USERS[username] == password:
            st.session_state["logged_in"] = True
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.error("❌ Incorrect ID or Password")

    return False