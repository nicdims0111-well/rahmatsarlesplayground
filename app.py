import streamlit as st
# import pandas as pd

st.set_page_config(
    page_title="cudai",
    page_icon="🦈",
    layout="wide",
    initial_sidebar_state="expanded",
    
)


USERS = {
    "admin": "admin123",
    "user1": "password1"
}

# Konfigurasi halaman


# Inisialisasi session_state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = None
if "data" not in st.session_state:
    st.session_state.data = None

# Login Page
if not st.session_state.authenticated:
    st.title("LINK BIRUUU NEW")
    st.subheader("INPUT WOI", divider=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if USERS.get(username) == password:
            st.session_state.authenticated = True
            st.session_state.username = username
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid username or password")
    st.stop()

