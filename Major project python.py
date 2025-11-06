import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

# ===== File name for saving =====
FILE_NAME = "expenses.csv"

# ===== Function: Load data =====
def load_data():
    if os.path.exists(FILE_NAME):
        return pd.read_csv(FILE_NAME, parse_dates=["date"])
    else:
        return pd.DataFrame(columns=["date", "category", "amount", "note"])

# ===== Function: Save data =====
def save_data(df):
    df.to_csv(FILE_NAME, index=False)

# ===== Initialize session state =====
if "df" not in st.session_state:
    st.session_state.df = load_data()

# ===== Sidebar form: Add expense =====
st.sidebar.header("➕ Add New Expense")
with st.sidebar.form("expense_form"):
    d = st.date_input("Date", datetime.today())
    cat = st.selectbox("Category", ["Food", "Travel", "Shopping", "Health", "Other"])
    amt = st.number_input("Amount (₹)", min_value=0.0, step=10.0)
    note = st.text_input("Note (optional)")
    submitted = st.form_submit_button("Add Expense")

    if submitted:
        new = {
            "date": pd.to_datetime(d),
            "category": cat,
            "amount": float(amt),
            "note": note
        }
        # ✅ Add new row with concat (instead of append)
        st.session_state.df = pd.concat(
            [st.session_state.df, pd.DataFrame([new])],
            ignore_index=True
        )
        save_data(st.session_state.df)
        st.sidebar.success("✅ Expense added!")

# ===== Main Dashboard =====
st.title("💰 Expense Tracker with Budget & Graphs")

if not st.session_state.df.empty:
    df = st.session_state.df

    # Show recent transactions
    st.subheader("🧾 Recent Transactions")
    st.dataframe(df.tail(50))

    # Budget setup
    st.subheader("💡 Budget Overview")
    daily_budget = st.number_input("Set Daily Budget (₹)", min_value=0.0, value=500.0, step=50.0)
    monthly_budget = st.number_input("Set Monthly Budget (₹)", min_value=0.0, value=15000.0, step=500.0)
    yearly_budget = st.number_input("Set Yearly Budget (₹)", min_value=0.0, value=200000.0, step=5000.0)

    today = pd.to_datetime(datetime.today().date())
    this_month = today.month
    this_year = today.year

    daily_spent = df[df["date"].dt.date == today.date()]["amount"].sum()
    monthly_spent = df[(df["date"].dt.month == this_month) & (df["date"].dt.year == this_year)]["amount"].sum()
    yearly_spent = df[df["date"].dt.year == this_year]["amount"].sum()

    st.progress(min(daily_spent/daily_budget, 1.0))
    st.write(f"📅 Today spent: ₹{daily_spent} / ₹{daily_budget}")

    st.progress(min(monthly_spent/monthly_budget, 1.0))
    st.write(f"🗓️ This Month spent: ₹{monthly_spent} / ₹{monthly_budget}")

    st.progress(min(yearly_spent/yearly_budget, 1.0))
    st.write(f"📆 This Year spent: ₹{yearly_spent} / ₹{yearly_budget}")

    # Charts
    st.subheader("📊 Visualizations")

    # Daily expenses (line chart)
    daily_exp = df.groupby("date")["amount"].sum()
    fig, ax = plt.subplots()
    daily_exp.plot(ax=ax, marker="o")
    ax.set_title("Daily Expenses")
    ax.set_ylabel("Amount (₹)")
    st.pyplot(fig)

    # Monthly expenses (bar chart)
    monthly_exp = df.groupby(df["date"].dt.to_period("M"))["amount"].sum()
    fig, ax = plt.subplots()
    monthly_exp.plot(kind="bar", ax=ax)
    ax.set_title("Monthly Expenses")
    ax.set_ylabel("Amount (₹)")
    st.pyplot(fig)

    # Category breakdown (pie chart)
    cat_exp = df.groupby("category")["amount"].sum()
    fig, ax = plt.subplots()
    cat_exp.plot(kind="pie", autopct="%1.1f%%", ax=ax)
    ax.set_ylabel("")
    ax.set_title("Spending by Category")
    st.pyplot(fig)

    # Download CSV
    st.subheader("⬇️ Download Data")
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "expenses.csv", "text/csv")
else:
    st.info("👉 No expenses yet! Add your first expense from the sidebar.")
