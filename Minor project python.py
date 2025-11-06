import streamlit as st
import pandas as pd
import os
from datetime import datetime
import matplotlib.pyplot as plt

# ===== File to store data =====
FILE_NAME = "expenses.csv"

# ===== Load Data =====
def load_data():
    if os.path.exists(FILE_NAME):
        return pd.read_csv(FILE_NAME, parse_dates=["date"])
    else:
        return pd.DataFrame(columns=["date", "category", "amount", "note"])

# ===== Save Data =====
def save_data(df):
    df.to_csv(FILE_NAME, index=False)

# ===== Initialize Session =====
if "df" not in st.session_state:
    st.session_state.df = load_data()

# ===== Sidebar: Add Expense =====
st.sidebar.header("➕ Add Expense")
with st.sidebar.form("form"):
    date = st.date_input("Date", datetime.today())
    category = st.selectbox("Category", ["Food", "Travel", "Shopping", "Health", "Other"])
    amount = st.number_input("Amount (₹)", min_value=0.0, step=10.0)
    note = st.text_input("Note")
    submit = st.form_submit_button("Add")

    if submit:
        new_row = {"date": date, "category": category, "amount": amount, "note": note}
        st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
        save_data(st.session_state.df)
        st.sidebar.success("Expense Added Successfully!")

# ===== Main App =====
st.title("💰 Simple Expense Tracker")

if not st.session_state.df.empty:
    df = st.session_state.df

    st.subheader("📋 Expense Records")
    st.dataframe(df.tail(20))

    # ===== Basic Analysis =====
    st.subheader("📊 Expense Summary")

    total = df["amount"].sum()
    st.write(f"**Total Spent:** ₹{total:.2f}")

    # ===== Category Chart =====
    cat_exp = df.groupby("category")["amount"].sum()
    fig, ax = plt.subplots()
    cat_exp.plot(kind="bar", ax=ax)
    ax.set_ylabel("Amount (₹)")
    ax.set_title("Spending by Category")
    st.pyplot(fig)

else:
    st.info("No expenses added yet. Use the sidebar to add one!")
