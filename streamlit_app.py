import streamlit as st

st.set_page_config(page_title="Login Demo", page_icon="🔐", layout="centered")

VALID_USERNAME = "demo"
VALID_PASSWORD = "password123"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("## 🔐 Login")
    st.write("Sign in with the demo account below to continue.")

    with st.form("login_form"):
        username = st.text_input("Username", key="username")
        password = st.text_input("Password", type="password", key="password")
        submitted = st.form_submit_button("Log in")

        if submitted:
            if username == VALID_USERNAME and password == VALID_PASSWORD:
                st.session_state.logged_in = True
                st.session_state.error_message = ""
                st.rerun()
            else:
                st.session_state.error_message = "Invalid username or password."

    if st.session_state.get("error_message"):
        st.error(st.session_state.error_message)

    st.caption("Demo credentials: demo / password123")
else:
    st.success("Login successful")
    st.title("Welcome to your dashboard")
    st.write("You are now signed in.")

    if st.button("Log out"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.password = ""
        st.session_state.error_message = ""
        st.rerun()
