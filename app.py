import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import os

def calculate_costs(df, agreement_term, months_remaining, payment_model):
    months_elapsed = agreement_term - months_remaining
    total_annual_cost = 0
    total_prepaid_cost = 0
    total_first_year_cost = 0
    total_annual_unit_fee = 0
    total_subscription_term_fee = 0
    total_updated_annual_cost = 0
    total_current_annual_services_fee = 0
    total_prepaid_total_cost = 0
    
    for index, row in df.iterrows():
        annual_total_fee = row['Unit Quantity'] * row['Annual Unit Fee']
        subscription_term_total_fee = (annual_total_fee * months_remaining) / 12
        co_termed_prepaid_cost = (row['Additional Licenses'] * row['Annual Unit Fee'] * months_remaining) / 12 if payment_model == 'Prepaid' else 0
        co_termed_first_year_cost = (row['Additional Licenses'] * row['Annual Unit Fee'] * (12 - (months_elapsed % 12))) / 12 if payment_model == 'Annual' else 0
        updated_annual_cost = annual_total_fee + (row['Additional Licenses'] * row['Annual Unit Fee']) if payment_model == 'Annual' else 0
        
        df.at[index, 'Current Annual Total Services Fee'] = f"${annual_total_fee:,.2f}"
        df.at[index, 'Prepaid Co-Termed Cost'] = f"${co_termed_prepaid_cost:,.2f}"
        df.at[index, 'First Year Co-Termed Cost'] = f"${co_termed_first_year_cost:,.2f}"
        df.at[index, 'Updated Annual Cost'] = f"${updated_annual_cost:,.2f}"
        df.at[index, 'Subscription Term Total Service Fee'] = f"${subscription_term_total_fee:,.2f}"
        
        total_annual_cost += updated_annual_cost
        total_prepaid_cost += co_termed_prepaid_cost
        total_first_year_cost += co_termed_first_year_cost
        total_annual_unit_fee += row['Annual Unit Fee'] * row['Unit Quantity']
        total_subscription_term_fee += subscription_term_total_fee
        total_updated_annual_cost += updated_annual_cost
        total_current_annual_services_fee += annual_total_fee
        total_prepaid_total_cost += co_termed_prepaid_cost
    
    return df, total_prepaid_cost, total_first_year_cost, total_annual_cost, total_annual_unit_fee, total_subscription_term_fee, total_updated_annual_cost, total_current_annual_services_fee, total_prepaid_total_cost

st.title("Co-Terming Cost Calculator")

st.subheader("Input Form")
customer_name = st.text_input("Customer Name:")
agreement_term = st.number_input("Agreement Term (Months):", min_value=1.0, value=36.0, step=0.01, format="%.2f")
months_remaining = st.number_input("Months Remaining:", min_value=0.01, max_value=agreement_term, value=30.0, step=0.01, format="%.2f")
payment_model = st.selectbox("Payment Model:", ["Prepaid", "Annual"])

st.subheader("Line Items")
if 'line_items' not in st.session_state:
    st.session_state.line_items = []

def add_line():
    st.session_state.line_items.append({
        "Cloud Service Description": "",
        "Unit Quantity": 0,
        "Annual Unit Fee": 0.0,
        "Additional Licenses": 0
    })

def remove_line():
    if st.session_state.line_items:
        st.session_state.line_items.pop()

st.button("➕ Add Line Item", on_click=add_line)
st.button("➖ Remove Last Line Item", on_click=remove_line)

data = pd.DataFrame(st.session_state.line_items)

st.write("### Line Items")
columns = ["Cloud Service Description", "Unit Quantity", "Annual Unit Fee", "Additional Licenses"]
col1, col2, col3, col4 = st.columns([3, 1, 2, 2])

for i, item in enumerate(st.session_state.line_items):
    item["Cloud Service Description"] = col1.text_input(f"Service {i+1}", value=item["Cloud Service Description"], key=f"service_{i}")
    item["Unit Quantity"] = col2.number_input(f"Qty {i+1}", min_value=0, value=item["Unit Quantity"], key=f"qty_{i}")
    item["Annual Unit Fee"] = col3.number_input(f"Fee {i+1} ($)", min_value=0.0, value=item["Annual Unit Fee"], step=0.01, format="%.2f", key=f"fee_{i}")
    item["Additional Licenses"] = col4.number_input(f"Add Licenses {i+1}", min_value=0, value=item["Additional Licenses"], key=f"add_lic_{i}")

data = pd.DataFrame(st.session_state.line_items)

if st.button("Calculate Results"):
    data, *_ = calculate_costs(data, agreement_term, months_remaining, payment_model)
    st.write("### Results")
    st.dataframe(data)
