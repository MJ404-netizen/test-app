import streamlit as st

st.set_page_config(page_title="Login Demo", page_icon="🔐", layout="centered")

VALID_USERNAME = "demo"
VALID_PASSWORD = "password123"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "show_forgot_password" not in st.session_state:
    st.session_state.show_forgot_password = False
if "show_create_account" not in st.session_state:
    st.session_state.show_create_account = False

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

    col1, col2 = st.columns(2)
    if col1.button("Forgot password?"):
        st.session_state.show_forgot_password = True
        st.session_state.show_create_account = False
    if col2.button("Create account"):
        st.session_state.show_create_account = True
        st.session_state.show_forgot_password = False

    if st.session_state.show_forgot_password:
        with st.expander("Reset your password", expanded=True):
            reset_email = st.text_input("Email address", key="reset_email")
            if st.button("Send reset link"):
                if reset_email:
                    st.success(f"A reset link would be sent to {reset_email}.")
                else:
                    st.warning("Please enter your email address.")

    if st.session_state.show_create_account:
        with st.expander("Create a new account", expanded=True):
            new_username = st.text_input("Choose a username", key="new_username")
            new_password = st.text_input("Create password", type="password", key="new_password")
            confirm_password = st.text_input("Confirm password", type="password", key="confirm_password")
            if st.button("Create account"):
                if not new_username or not new_password:
                    st.warning("Please fill in all fields.")
                elif new_password != confirm_password:
                    st.warning("Passwords do not match.")
                else:
                    st.success(f"Account for {new_username} created successfully.")

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
