import streamlit as st
import pandas as pd
import altair as alt
from datetime import date
import os

# ----------------------------
# 🌙 DARK/LIGHT MODE TOGGLE
# ----------------------------
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

toggle = st.toggle("🌙 Dark Mode", key="dark_toggle")
st.session_state.dark_mode = toggle

if st.session_state.dark_mode:
    st.markdown("""
        <style>
            body {
                background-color: #0e1117;
                color: white;
            }
            .stApp {
                background-color: #0e1117;
                color: white;
            }
        </style>
    """, unsafe_allow_html=True)

# ----------------------------
# 💰 EXPENSE TRACKER (ONLY)
# ----------------------------
st.set_page_config(page_title="💸 Expense Tracker", layout="wide")
st.title("🧾 Personal Expense Tracker (Expenses Only)")

# Load previous data if file exists
csv_file = "expenses.csv"
if "expenses" not in st.session_state:
    if os.path.exists(csv_file):
        st.session_state.expenses = pd.read_csv(csv_file).to_dict("records")
    else:
        st.session_state.expenses = []

# ----------------------------
# ➕ ADD EXPENSE FORM
# ----------------------------
with st.sidebar:
    st.header("➕ Add Expense")
    category = st.selectbox("Category", ["Food", "Rent", "Shopping", "Bills", "Travel", "Other"])
    amount = st.number_input("Amount Spent", min_value=0.0, format="%.2f")
    note = st.text_input("Optional Note")
    date_entry = st.date_input("Date", value=date.today())
    add = st.button("✅ Add Expense")

    if add and amount > 0:
        new_expense = {
            "Category": category,
            "Amount": amount,
            "Note": note,
            "Date": date_entry.strftime("%Y-%m-%d")
        }
        st.session_state.expenses.append(new_expense)
        pd.DataFrame(st.session_state.expenses).to_csv(csv_file, index=False)
        st.success("Expense added!")

# ----------------------------
# 📋 VIEW & MANAGE EXPENSES
# ----------------------------
st.subheader("📋 All Expenses")

if st.session_state.expenses:
    df = pd.DataFrame(st.session_state.expenses)
    df["Date"] = pd.to_datetime(df["Date"])
    df.sort_values("Date", inplace=True)

    delete_indices = []
    for i, row in df.iterrows():
        col1, col2 = st.columns([0.9, 0.1])
        with col1:
            st.markdown(
                f"**{row['Date'].date()}** | 💰 ₹{row['Amount']} | 📂 {row['Category']} - {row['Note']}"
            )
        with col2:
            if st.button("❌", key=f"del_{i}"):
                delete_indices.append(i)

    # Apply deletions
    if delete_indices:
        df.drop(index=delete_indices, inplace=True)
        st.session_state.expenses = df.to_dict("records")
        pd.DataFrame(st.session_state.expenses).to_csv(csv_file, index=False)
        st.rerun()

    st.markdown("---")

    # ----------------------------
    # 📊 EXPENSES BY CATEGORY
    # ----------------------------
    st.subheader("📊 Breakdown by Category")
    pie_data = df.groupby("Category", as_index=False)["Amount"].sum()

    pie_chart = alt.Chart(pie_data).mark_arc().encode(
        theta="Amount:Q",
        color="Category:N",
        tooltip=["Category", "Amount"]
    ).properties(width=400, height=400)

    st.altair_chart(pie_chart, use_container_width=True)

    # ----------------------------
    # 📈 DAILY EXPENSE TREND
    # ----------------------------
    st.subheader("📈 Daily Expenses")
    daily_data = df.groupby("Date", as_index=False)["Amount"].sum()

    line_chart = alt.Chart(daily_data).mark_line(point=True).encode(
        x="Date:T",
        y="Amount:Q",
        tooltip=["Date", "Amount"]
    ).properties(height=300)

    st.altair_chart(line_chart, use_container_width=True)

    # ----------------------------
    # ⬇️ DOWNLOAD DATA
    # ----------------------------
    st.subheader("⬇️ Download Expense Data")
    csv_data = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download CSV", csv_data, "expenses.csv", "text/csv")
else:
    st.info("No expenses yet. Add from the sidebar ➡️")
