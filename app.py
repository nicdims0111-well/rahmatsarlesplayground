import streamlit as st
# import pandas as pd

st.set_page_config(
    page_title="cudai",
    page_icon="🦈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

USERS = {
    "admin": "admin123",
    "user1": "password1"
}

# Konfigurasi halaman
st.set_page_config(page_title="Personal Finance Dashboard", layout="wide")

# Inisialisasi session_state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = None
if "data" not in st.session_state:
    st.session_state.data = None

# Login Page
if not st.session_state.authenticated:
    st.title("🔐 Login Page")
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

