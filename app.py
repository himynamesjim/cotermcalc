import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF

def calculate_costs(df, agreement_term, months_remaining, payment_model):
    months_elapsed = agreement_term - months_remaining
    total_annual_cost = 0
    total_prepaid_cost = 0
    total_first_year_cost = 0
    total_updated_annual_cost = 0
    total_subscription_term_fee = 0
    total_annual_unit_fee = df['Annual Unit Fee'].sum()
    
    for index, row in df.iterrows():
        annual_total_fee = row['Unit Quantity'] * row['Annual Unit Fee']
        subscription_term_total_fee = ((annual_total_fee * months_remaining) / 12) + ((row['Additional Licenses'] * row['Annual Unit Fee'] * months_remaining) / 12)
        co_termed_prepaid_cost = (row['Additional Licenses'] * row['Annual Unit Fee'] * months_remaining) / 12 if payment_model == 'Prepaid' else 0
        co_termed_first_year_cost = (row['Additional Licenses'] * row['Annual Unit Fee'] * (12 - (months_elapsed % 12))) / 12 if payment_model == 'Annual' else 0
        updated_annual_cost = annual_total_fee + (row['Additional Licenses'] * row['Annual Unit Fee']) if payment_model == 'Annual' else 0
        
        df.at[index, 'Prepaid Co-Termed Cost'] = co_termed_prepaid_cost
        df.at[index, 'First Year Co-Termed Cost'] = co_termed_first_year_cost
        df.at[index, 'Updated Annual Cost'] = updated_annual_cost
        df.at[index, 'Subscription Term Total Service Fee'] = subscription_term_total_fee
        
        total_annual_cost += updated_annual_cost
        total_prepaid_cost += co_termed_prepaid_cost
        total_first_year_cost += co_termed_first_year_cost
        total_subscription_term_fee += subscription_term_total_fee
    
    total_row = pd.DataFrame({
        "Cloud Service Description": ["Total Services Cost"],
        "Unit Quantity": ["-"],
        "Annual Unit Fee": [f"${total_annual_unit_fee:,.2f}"],
        "Additional Licenses": ["-"],
        "Prepaid Co-Termed Cost": [f"${total_prepaid_cost:,.2f}"],
        "First Year Co-Termed Cost": [f"${total_first_year_cost:,.2f}"],
        "Updated Annual Cost": [f"${total_updated_annual_cost:,.2f}"],
        "Subscription Term Total Service Fee": [f"${total_subscription_term_fee:,.2f}"]
    })
    df = pd.concat([df, total_row], ignore_index=True)
    
    return df, total_prepaid_cost, total_first_year_cost, total_updated_annual_cost, total_subscription_term_fee

def generate_pdf(customer_name, billing_term, months_remaining, total_prepaid_cost, total_first_year_cost, total_updated_annual_cost, total_subscription_term_fee, data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 10)
    pdf.cell(200, 8, "Co-Terming Cost Report", ln=True, align="C")
    pdf.ln(4)
    
    pdf.set_font("Arial", "", 8)
    pdf.cell(200, 5, f"Date: {datetime.today().strftime('%Y-%m-%d')}", ln=True)
    pdf.cell(200, 5, f"Customer Name: {customer_name}", ln=True)
    pdf.cell(200, 5, f"Billing Term: {billing_term}", ln=True)
    pdf.cell(200, 5, f"Subscription Term Remaining Months: {months_remaining:.2f}", ln=True)
    pdf.cell(200, 5, f"Total Pre-Paid Cost: ${total_prepaid_cost:,.2f}", ln=True)
    pdf.cell(200, 5, f"First Year Co-Termed Cost: ${total_first_year_cost:,.2f}", ln=True)
    pdf.cell(200, 5, f"Updated Annual Cost: ${total_updated_annual_cost:,.2f}", ln=True)
    pdf.cell(200, 5, f"Subscription Term Total Service Fee: ${total_subscription_term_fee:,.2f}", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 7)
    pdf.cell(200, 5, "Detailed Line Items", ln=True)
    pdf.set_font("Arial", "", 5)
    
    headers = list(data.columns)
    col_widths = [35, 15, 20, 15, 25, 25, 25, 25]
    
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 4, header, border=1, align="C")
    pdf.ln()
    
    pdf.set_font("Arial", "", 5)
    for _, row in data.iterrows():
        for i, col in enumerate(headers):
            text = str(row[col])
            pdf.cell(col_widths[i], 4, text, border=1, align="C")
        pdf.ln()
    
    pdf_filename = "coterming_report.pdf"
    pdf.output(pdf_filename)
    return pdf_filename

st.title("Co-Terming Cost Calculator")

st.subheader("Results")
if st.button("Calculate Costs"):
    data, total_prepaid_cost, total_first_year_cost, total_updated_annual_cost, total_subscription_term_fee = calculate_costs(data, agreement_term, months_remaining, payment_model)
    st.subheader("Detailed Line Items")
    st.dataframe(data.style.format({
        "Annual Unit Fee": "${:,.2f}",
        "Prepaid Co-Termed Cost": "${:,.2f}",
        "First Year Co-Termed Cost": "${:,.2f}",
        "Updated Annual Cost": "${:,.2f}",
        "Subscription Term Total Service Fee": "${:,.2f}"
    }).set_properties(**{"white-space": "normal"}))
    pdf_path = generate_pdf(customer_name, billing_term, months_remaining, total_prepaid_cost, total_first_year_cost, total_updated_annual_cost, total_subscription_term_fee, data)
    with open(pdf_path, "rb") as file:
        st.download_button(label="Download PDF", data=file, file_name="coterming_report.pdf", mime="application/pdf")
