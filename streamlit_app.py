import streamlit as st

st.set_page_config(page_title="Login Demo", page_icon="🔐")

VALID_USERNAME = "demo"
VALID_PASSWORD = "password123"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:

    st.title("🔐 Login")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log in")

        if submitted:
            if username == VALID_USERNAME and password == VALID_PASSWORD:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid username or password.")

    col1, col2 = st.columns(2)

    with col1:
        st.button("Forgot Password")

    with col2:
        if st.button("Create Account"):
            st.switch_page("create_account.py")

else:
    st.success("Login successful!")
    st.title("Dashboard")

    if st.button("Log out"):
        st.session_state.logged_in = False
        st.rerun()