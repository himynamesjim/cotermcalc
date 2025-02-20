import streamlit as st
import os
import pandas as pd

st.title("Customer Agreements")

# Define the directory where customer data is stored
CUSTOMER_DATA_DIR = "customer_data"
os.makedirs(CUSTOMER_DATA_DIR, exist_ok=True)

# Get a list of all customer files
customer_files = [f.replace(".csv", "") for f in os.listdir(CUSTOMER_DATA_DIR) if f.endswith(".csv")]

if "selected_customer" not in st.session_state:
    st.session_state["selected_customer"] = None

if customer_files:
    selected_customer = st.selectbox("Select a Customer", customer_files)

    if st.button("View Agreement"):
        st.session_state["selected_customer"] = selected_customer
        st.experimental_rerun()  # Forces the app to refresh to show the selected customer

# Redirect to customer_detail.py when a customer is selected
if st.session_state["selected_customer"]:
    st.write(f"Loading agreement for {st.session_state['selected_customer']}...")
    st.markdown("[Go to Customer Agreement](pages/customer_detail.py)")
else:
    st.write("Select a customer to view their agreement.")
