import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime

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
        
        df.at[index, 'Current Annual Total Services Fee'] = annual_total_fee
        df.at[index, 'Prepaid Co-Termed Cost'] = co_termed_prepaid_cost
        df.at[index, 'First Year Co-Termed Cost'] = co_termed_first_year_cost
        df.at[index, 'Updated Annual Cost'] = updated_annual_cost
        df.at[index, 'Subscription Term Total Service Fee'] = subscription_term_total_fee
        
        total_annual_cost += updated_annual_cost
        total_prepaid_cost += co_termed_prepaid_cost
        total_first_year_cost += co_termed_first_year_cost
        total_annual_unit_fee += row['Annual Unit Fee']
        total_subscription_term_fee += subscription_term_total_fee
        total_updated_annual_cost += updated_annual_cost
        total_current_annual_services_fee += annual_total_fee
        total_prepaid_total_cost += co_termed_prepaid_cost
    
    return df, total_prepaid_cost, total_first_year_cost, total_annual_cost, total_annual_unit_fee, total_subscription_term_fee, total_updated_annual_cost, total_current_annual_services_fee, total_prepaid_total_cost

def generate_pdf(data, total_prepaid_total_cost, total_first_year, total_updated_annual_cost, total_subscription_term_fee, customer_name, agreement_term, months_remaining):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Add Logo
    logo_path = "logo.png"  # Ensure this image is available in the working directory
    pdf.image(logo_path, x=10, y=8, w=30)
    pdf.ln(20)  # Space after logo
    
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
    pdf.cell(200, 10, f"Total Pre-Paid Cost: ${total_prepaid_total_cost:,.2f}", ln=True)
    pdf.cell(200, 10, f"First Year Co-Termed Cost: ${total_first_year:,.2f}", ln=True)
    pdf.cell(200, 10, f"Updated Annual Cost: ${total_updated_annual_cost:,.2f}", ln=True)
    pdf.cell(200, 10, f"Subscription Term Total Service Fee: ${total_subscription_term_fee:,.2f}", ln=True)
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
num_items = st.number_input("Number of Line Items:", min_value=1, value=1)

st.subheader("Enter License Information")
columns = ["Cloud Service Description", "Unit Quantity", "Annual Unit Fee", "Additional Licenses", "Current Annual Total Services Fee", "Prepaid Co-Termed Cost", "First Year Co-Termed Cost", "Updated Annual Cost", "Subscription Term Total Service Fee"]
data = pd.DataFrame(columns=columns)

for i in range(num_items):
    row_data = {}
    st.markdown(f"**Item {i+1}**")
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    row_data["Cloud Service Description"] = col1.text_input(f"Service {i+1}", key=f"service_{i}")
    row_data["Unit Quantity"] = col2.number_input(f"Qty {i+1}", min_value=0, value=0, key=f"qty_{i}")
    row_data["Annual Unit Fee"] = col3.number_input(f"Fee {i+1} ($)", min_value=0.0, value=0.0, step=0.01, format="%.2f", key=f"fee_{i}")
    row_data["Additional Licenses"] = col4.number_input(f"Add Licenses {i+1}", min_value=0, value=0, key=f"add_lic_{i}")
    
    new_row = pd.DataFrame([row_data])
    data = pd.concat([data, new_row], ignore_index=True)

st.subheader("Results")
if st.button("Calculate Costs"):
    data, total_prepaid, total_first_year, total_annual, total_annual_unit_fee, total_subscription_term_fee, total_updated_annual_cost, total_current_annual_services_fee, total_prepaid_total_cost = calculate_costs(data, agreement_term, months_remaining, payment_model)
    
    pdf_data = generate_pdf(data, total_prepaid_total_cost, total_first_year, total_updated_annual_cost, total_subscription_term_fee, customer_name, agreement_term, months_remaining)
    st.download_button("Download PDF Report", pdf_data, "co_terming_cost_report.pdf", "application/pdf")
