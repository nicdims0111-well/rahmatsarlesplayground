# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime


# Dummy user data (untuk simulasi login)
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

# Sidebar Navigation
page = st.sidebar.selectbox(
    "📄 Go to Page",
    ("Dashboard", "Upload Data", "Finance Chatbot", "Settings")
)





# Sample chatbot reply
def finance_bot(question, df):
    if df is None:
        return "Please upload your data first."
    if "pengeluaran terbesar" in question.lower():
        max_row = df.loc[df["Amount"].idxmin()]
        return f"Pengeluaran terbesar Anda adalah {abs(max_row['Amount']):,.0f} untuk {max_row['Category']} pada {max_row['Date']}."
    return "Maaf, saya belum memahami pertanyaan Anda sepenuhnya."


# Dashboard Page
if page == "Dashboard":
    st.title("📊 Personal Finance Dashboard")
    if st.session_state.data is None:
        st.info("Please upload your transaction data first on the 'Upload Data' page.")
    else:
        df = st.session_state.data
        total_income = df[df["Amount"] > 0]["Amount"].sum()
        total_expense = df[df["Amount"] < 0]["Amount"].sum()
        net_balance = total_income + total_expense

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Income", f"Rp {total_income:,.0f}")
        col2.metric("Total Expense", f"Rp {abs(total_expense):,.0f}")
        col3.metric("Net Balance", f"Rp {net_balance:,.0f}")

        st.subheader("📈 Monthly Expenses")
        df["Month"] = pd.to_datetime(df["Date"]).dt.to_period("M").astype(str)
        monthly = df[df["Amount"] < 0].groupby("Month")["Amount"].sum().reset_index()
        fig = px.bar(monthly, x="Month", y="Amount", title="Monthly Expenses", labels={'Amount':'Total Expense'})
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📊 Expense by Category")
        category = df[df["Amount"] < 0].groupby("Category")["Amount"].sum().reset_index()
        fig2 = px.bar(category, x="Category", y="Amount", title="Expenses by Category", labels={'Amount':'Total Expense'})
        st.plotly_chart(fig2, use_container_width=True)


# Upload Page
elif page == "Upload Data":
    st.title("📁 Upload Your Financial Transactions")
    st.markdown("Format file: CSV dengan kolom `Date`, `Amount`, `Category`")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            df["Date"] = pd.to_datetime(df["Date"])
            st.dataframe(df.head())
            st.session_state.data = df
            st.success("Data uploaded successfully!")
        except Exception as e:
            st.error(f"Error loading data: {e}")

# Chatbot Page
elif page == "Finance Chatbot":
    st.title("💬 Ask Our Finance Bot")
    st.chat_message("assistant").write("Hi! Saya adalah FinanceBot. Tanyakan apapun seputar keuangan Anda!")
    if prompt := st.chat_input("Tulis pertanyaan Anda..."):
        st.chat_message("user").write(prompt)
        response = finance_bot(prompt, st.session_state.data)
        st.chat_message("assistant").write(response)

