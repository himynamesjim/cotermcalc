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
    
    return df, f"${total_prepaid_cost:,.2f}", f"${total_first_year_cost:,.2f}", f"${total_annual_cost:,.2f}", f"${total_annual_unit_fee:,.2f}", f"${total_subscription_term_fee:,.2f}", f"${total_updated_annual_cost:,.2f}", f"${total_current_annual_services_fee:,.2f}", f"${total_prepaid_total_cost:,.2f}"

def generate_pdf(data, customer_name, agreement_term, months_remaining, total_prepaid_total_cost, total_first_year_cost, total_updated_annual_cost, total_subscription_term_fee):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Co-Terming Cost Report", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "Summary", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, f"Date: {datetime.now().strftime('%Y-%m-%d')}", ln=True)
    pdf.cell(200, 10, f"Customer Name: {customer_name}", ln=True)
    pdf.cell(200, 10, f"Billing Term (Agreement Term): {agreement_term} months", ln=True)
    pdf.cell(200, 10, f"Subscription Term Remaining Months: {months_remaining:.2f}", ln=True)
    pdf.cell(200, 10, f"Total Pre-Paid Cost: {total_prepaid_total_cost}", ln=True)
    pdf.cell(200, 10, f"First Year Co-Termed Cost: {total_first_year_cost}", ln=True)
    pdf.cell(200, 10, f"Updated Annual Cost: {total_updated_annual_cost}", ln=True)
    pdf.cell(200, 10, f"Subscription Term Total Service Fee: {total_subscription_term_fee}", ln=True)
    pdf.ln(10)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "Detailed Line Items", ln=True)
    pdf.set_font("Arial", "", 10)
    
    for index, row in data.iterrows():
        pdf.cell(200, 10, f"Service: {row['Cloud Service Description']} - Qty: {row['Unit Quantity']} - Fee: {row['Annual Unit Fee']} - Prepaid Cost: {row['Prepaid Co-Termed Cost']}", ln=True)
    
    return pdf.output(dest='S').encode('latin1')

st.title("Co-Terming Cost Calculator")

st.subheader("Input Form")
customer_name = st.text_input("Customer Name:")
agreement_term = st.number_input("Agreement Term (Months):", min_value=1.0, value=36.0, step=0.01, format="%.2f")
months_remaining = st.number_input("Months Remaining:", min_value=0.01, max_value=agreement_term, value=30.0, step=0.01, format="%.2f")
payment_model = st.selectbox("Payment Model:", ["Prepaid", "Annual"])
num_items = st.number_input("Number of Line Items:", min_value=1, value=1, step=1)

data = pd.DataFrame(columns=["Cloud Service Description", "Unit Quantity", "Annual Unit Fee", "Additional Licenses"])

for i in range(int(num_items)):
    st.markdown(f"**Item {i+1}**")
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    row_data = {
        "Cloud Service Description": col1.text_input(f"Service {i+1}", key=f"service_{i}"),
        "Unit Quantity": col2.number_input(f"Qty {i+1}", min_value=0, value=0, key=f"qty_{i}"),
        "Annual Unit Fee": col3.number_input(f"Fee {i+1} ($)", min_value=0.0, value=0.0, step=0.01, format="%.2f", key=f"fee_{i}"),
        "Additional Licenses": col4.number_input(f"Add Licenses {i+1}", min_value=0, value=0, key=f"add_lic_{i}")
    }
    data = pd.concat([data, pd.DataFrame([row_data])], ignore_index=True)

if st.button("Calculate Results"):
    data, total_prepaid, total_first_year, total_annual, total_annual_unit_fee, total_subscription_term_fee, total_updated_annual_cost, total_current_annual_services_fee, total_prepaid_total_cost = calculate_costs(data, agreement_term, months_remaining, payment_model)
    st.write("### Results")
    st.dataframe(data)
    
    pdf_data = generate_pdf(data, customer_name, agreement_term, months_remaining, total_prepaid_total_cost, total_first_year, total_updated_annual_cost, total_subscription_term_fee)
    st.download_button("Download PDF Report", pdf_data, "co_terming_cost_report.pdf", "application/pdf")
