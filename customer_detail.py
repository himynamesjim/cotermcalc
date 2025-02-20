import streamlit as st
import pandas as pd
from fpdf import FPDF
import os
from datetime import datetime

st.title("Customer Agreement Details")

# Check if a customer is selected
if "selected_customer" not in st.session_state or not st.session_state["selected_customer"]:
    st.error("No customer selected. Please return to the home page.")
    st.stop()

customer_name = st.session_state["selected_customer"]
customer_file = os.path.join("customer_data", f"{customer_name}.csv")

st.subheader(f"Agreement for {customer_name}")

# Load customer data
if os.path.exists(customer_file):
    data = pd.read_csv(customer_file)
else:
    st.error("Customer data not found.")
    st.stop()

# Display and edit agreement data
st.dataframe(data)

# Allow modifications
st.subheader("Update Agreement")
for i, row in data.iterrows():
    data.at[i, "Unit Quantity"] = st.number_input(f"Quantity {i+1}", value=int(row["Unit Quantity"]))
    data.at[i, "Annual Unit Fee"] = st.number_input(f"Annual Unit Fee {i+1}", value=float(row["Annual Unit Fee"]), format="%.2f")

# Save changes
if st.button("Save Updates"):
    data.to_csv(customer_file, index=False)
    st.success("Agreement updated successfully.")

# Function to generate a PDF
def generate_pdf(data, customer_name):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Add title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, f"Agreement Report for {customer_name}", ln=True, align='C')
    pdf.ln(10)
    
    # Add agreement details
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "Agreement Details", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, f"Date: {datetime.now().strftime('%Y-%m-%d')}", ln=True)
    pdf.cell(200, 10, f"Customer: {customer_name}", ln=True)
    pdf.ln(10)
    
    # Table Header
    pdf.set_font("Arial", "B", 10)
    pdf.cell(60, 10, "Service Description", 1)
    pdf.cell(40, 10, "Quantity", 1)
    pdf.cell(40, 10, "Annual Fee", 1)
    pdf.cell(40, 10, "Total Cost", 1)
    pdf.ln()

    # Add data rows
    pdf.set_font("Arial", "", 10)
    for _, row in data.iterrows():
        pdf.cell(60, 10, row["Cloud Service Description"], 1)
        pdf.cell(40, 10, str(row["Unit Quantity"]), 1)
        pdf.cell(40, 10, f"${row['Annual Unit Fee']:.2f}", 1)
        pdf.cell(40, 10, f"${row['Unit Quantity'] * row['Annual Unit Fee']:.2f}", 1)
        pdf.ln()
    
    return pdf.output(dest='S').encode('latin1')

# Generate and download PDF
if st.button("Download Agreement PDF"):
    pdf_data = generate_pdf(data, customer_name)
    st.download_button("Download PDF", pdf_data, f"{customer_name}_agreement.pdf", "application/pdf")

# Go back to the home page
if st.button("Back to Home"):
    st.session_state["selected_customer"] = None
    st.experimental_rerun()
