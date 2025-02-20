import streamlit as st
import os
import pandas as pd

st.title("Customer Agreements")

# Define the directory where customer data is stored
CUSTOMER_DATA_DIR = "customer_data"
os.makedirs(CUSTOMER_DATA_DIR, exist_ok=True)

# Get a list of all customer files
customer_files = [f.replace(".csv", "") for f in os.listdir(CUSTOMER_DATA_DIR) if f.endswith(".csv")]

if customer_files:
    selected_customer = st.selectbox("Select a Customer", customer_files)

    if st.button("View Agreement"):
        st.session_state["selected_customer"] = selected_customer
        st.switch_page("pages/customer_detail.py")  # Navigate to the detail page
else:
    st.write("No customer agreements found.")
