import streamlit as st

st.set_page_config(page_title="Create Account", page_icon="📝")

st.title("📝 Create Account")

username = st.text_input("Choose a username")
password = st.text_input("Create password", type="password")
confirm = st.text_input("Confirm password", type="password")

if st.button("Create Account"):

    if not username or not password:
        st.warning("Please fill in all fields.")

    elif password != confirm:
        st.warning("Passwords do not match.")

    else:
        st.success(f"Account '{username}' created successfully!")

if st.button("← Back to Login"):
    st.switch_page("app.py")