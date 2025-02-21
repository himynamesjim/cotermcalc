"Updated Annual Cost": [f"${total_updated_annual_cost:,.2f}"]
        "Subscription Term Total Service Fee": [f"${total_subscription_term_fee:,.2f}"],
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
    col_widths = [35, 15, 20, 15, 25, 25, 25, 25, 25, 25]
    
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

st.subheader("Input Form")
current_date = datetime.today().strftime('%Y-%m-%d')
st.text(f"Date: {current_date}")
customer_name = st.text_input("Customer Name:")
billing_term = st.selectbox("Billing Term:", ["Annual", "Prepaid", "Monthly"])
agreement_term = st.number_input("Agreement Term (Months):", min_value=1, value=36, step=1, format="%d")
months_remaining = st.number_input("Months Remaining:", min_value=0.01, max_value=float(agreement_term), value=30.0, step=0.01, format="%.2f")

num_items = st.number_input("Number of Line Items:", min_value=1, value=1, step=1, format="%d")

st.subheader("Enter License Information")
columns = ["Cloud Service Description", "Unit Quantity", "Annual Unit Fee", "Additional Licenses", "Prepaid Co-Termed Cost", "Prepaid Additional Licenses Co-Termed Cost", "First Year Co-Termed Cost", "Updated Annual Cost", "Subscription Term Total Service Fee", "Monthly Co-Termed Cost", "First Month Co-Termed Cost", "Remaining Prepaid Cost"]
data = pd.DataFrame(columns=columns)

for i in range(num_items):
    row_data = {}
    st.markdown(f"**Item {i+1}**")
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    row_data["Cloud Service Description"] = col1.text_input(f"Service {i+1}", key=f"service_{i}")
    row_data["Unit Quantity"] = col2.number_input(f"Qty {i+1}", min_value=0, value=0, step=1, format="%d", key=f"qty_{i}")
    row_data["Annual Unit Fee"] = col3.number_input(f"Fee {i+1} ($)", min_value=0.0, value=0.0, step=0.01, format="%.2f", key=f"fee_{i}")
    row_data["Additional Licenses"] = col4.number_input(f"Add Licenses {i+1}", min_value=0, value=0, step=1, format="%d", key=f"add_lic_{i}")
    
    new_row = pd.DataFrame([row_data])
    data = pd.concat([data, new_row], ignore_index=True)

st.subheader("Results")
if st.button("Calculate Costs"):
    data, total_prepaid_cost, total_first_year_cost, total_updated_annual_cost, total_subscription_term_fee = calculate_costs(data, agreement_term, months_remaining, billing_term)
    st.subheader("Detailed Line Items")
    if billing_term == 'Monthly':
        data = data.drop(columns=['Prepaid Co-Termed Cost', 'First Year Co-Termed Cost', 'Updated Annual Cost'])
    elif billing_term == 'Annual':
        data = data.drop(columns=['Prepaid Co-Termed Cost'])
        data = data.drop(columns=['Monthly Co-Termed Cost', 'First Month Co-Termed Cost'])
    elif billing_term == 'Prepaid':
        data = data.drop(columns=['Monthly Co-Termed Cost', 'First Month Co-Termed Cost', 'First Year Co-Termed Cost', 'Updated Annual Cost', 'Prepaid Co-Termed Cost', 'Remaining Prepaid Cost'])
    data = data.copy()
    for col in ["Annual Unit Fee", "Prepaid Co-Termed Cost", "Prepaid Additional Licenses Co-Termed Cost", "First Year Co-Termed Cost", "Updated Annual Cost", "Subscription Term Total Service Fee", "Monthly Co-Termed Cost", "First Month Co-Termed Cost"]:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors='coerce')
    
    st.dataframe(data.style.format({
        "Annual Unit Fee": "${:,.2f}",
        "Prepaid Co-Termed Cost": "${:,.2f}",
        "Prepaid Additional Licenses Co-Termed Cost": "${:,.2f}",
        "First Year Co-Termed Cost": "${:,.2f}",
        "Updated Annual Cost": "${:,.2f}",
        "Subscription Term Total Service Fee": "${:,.2f}",
        "Monthly Co-Termed Cost": "${:,.2f}",
        "First Month Co-Termed Cost": "${:,.2f}"
    }).set_properties(**{"white-space": "normal"}))
    pdf_path = generate_pdf(customer_name, billing_term, months_remaining, total_prepaid_cost, total_first_year_cost, total_updated_annual_cost, total_subscription_term_fee, data)
    with open(pdf_path, "rb") as file:
        st.download_button(label="Download PDF", data=file, file_name="coterming_report.pdf", mime="application/pdf")
