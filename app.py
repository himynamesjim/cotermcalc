import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF

# At the top of your file with other imports
import streamlit.components.v1 as components

# After your imports, add this constant for the chart HTML/JS
CHART_HTML = """
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0"></script>
</head>
<body>
    <canvas id="costChart" style="width: 100%; height: 400px;"></canvas>
    
    <script>
        Chart.register(ChartDataLabels);
        
        function renderChart(data, billingTerm) {
            const ctx = document.getElementById('costChart').getContext('2d');
            
            let datasets = [];
            
            if (billingTerm === 'Monthly') {
                datasets = [
                    {
                        label: 'Co-Termed Monthly Cost',
                        data: [data.coTermedMonthly || 0],
                        backgroundColor: '#8884d8'
                    },
                    {
                        label: 'New Monthly Cost',
                        data: [data.newMonthly || 0],
                        backgroundColor: '#82ca9d'
                    },
                    {
                        label: 'Total Subscription Cost',
                        data: [data.subscription || 0],
                        backgroundColor: '#ffc658'
                    }
                ];
            } else if (billingTerm === 'Annual') {
                datasets = [
                    {
                        label: 'First Year Co-Termed Cost',
                        data: [data.firstYearCoTerm],
                        backgroundColor: '#8884d8'
                    },
                    {
                        label: 'New Annual Cost',
                        data: [data.newAnnual],
                        backgroundColor: '#82ca9d'
                    },
                    {
                        label: 'Total Subscription Cost',
                        data: [data.subscription],
                        backgroundColor: '#ffc658'
                    }
                ];
            } else if (billingTerm === 'Prepaid') {
                datasets = [
                    {
                        label: 'Co-Termed Prepaid Cost',
                        data: [data.coTermedPrepaid],
                        backgroundColor: '#8884d8'
                    }
                ];
            }

            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['Cost Comparison'],
                    datasets: datasets
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        datalabels: {
                            anchor: 'end',
                            align: 'top',
                            formatter: function(value) {
                                return '$' + value.toLocaleString(undefined, {
                                    minimumFractionDigits: 2,
                                    maximumFractionDigits: 2
                                });
                            },
                            font: {
                                weight: 'bold',
                                size: 12
                            },
                            offset: 5
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    let value = context.raw;
                                    return `${context.dataset.label}: $${value.toLocaleString(undefined, {
                                        minimumFractionDigits: 2,
                                        maximumFractionDigits: 2
                                    })}`;
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return '$' + value.toLocaleString();
                                }
                            }
                        }
                    }
                }
            });
        }
    </script>
</body>
</html>
"""

def calculate_costs(df, agreement_term, months_remaining, extension_months, billing_term):
    total_term = months_remaining + extension_months
    months_elapsed = agreement_term - months_remaining
    total_prepaid_cost = 0
    total_first_year_cost = 0
    total_updated_annual_cost = 0
    total_subscription_term_fee = 0

    for index, row in df.iterrows():
        first_month_co_termed_cost = (row['Annual Unit Fee'] / 12) * row['Additional Licenses'] * (months_remaining % 1) if billing_term == 'Monthly' else 0
        monthly_co_termed_cost = (row['Annual Unit Fee'] / 12) * row['Additional Licenses'] if billing_term == 'Monthly' else 0
        annual_total_fee = row['Unit Quantity'] * row['Annual Unit Fee']
        subscription_term_total_fee = ((annual_total_fee * total_term) / 12) + ((row['Additional Licenses'] * row['Annual Unit Fee'] * total_term) / 12)
        co_termed_prepaid_cost = (row['Additional Licenses'] * row['Annual Unit Fee'] * total_term) / 12 if billing_term == 'Prepaid' else 0
        co_termed_prepaid_additional_cost = (row['Additional Licenses'] * row['Annual Unit Fee'] * total_term) / 12 if billing_term == 'Prepaid' else 0
        co_termed_first_year_cost = (row['Additional Licenses'] * row['Annual Unit Fee'] * (12 - (months_elapsed % 12))) / 12 if billing_term == 'Annual' else 0
        updated_annual_cost = annual_total_fee + (row['Additional Licenses'] * row['Annual Unit Fee']) if billing_term == 'Annual' else 0

        df.at[index, 'Prepaid Co-Termed Cost'] = co_termed_prepaid_cost
        df.at[index, 'First Year Co-Termed Cost'] = co_termed_first_year_cost
        df.at[index, 'Updated Annual Cost'] = updated_annual_cost
        df.at[index, 'Subscription Term Total Service Fee'] = subscription_term_total_fee
        df.at[index, 'First Month Co-Termed Cost'] = first_month_co_termed_cost
        df.at[index, 'Monthly Co-Termed Cost'] = monthly_co_termed_cost

    # Convert numeric columns to float
    numeric_cols = [
        "Annual Unit Fee", "Prepaid Co-Termed Cost",
        "First Year Co-Termed Cost", "Updated Annual Cost", "Subscription Term Total Service Fee",
        "Monthly Co-Termed Cost", "First Month Co-Termed Cost"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Create Total Services Cost row
    total_row = pd.DataFrame({
        "Cloud Service Description": ["Total Services Cost"],
        "Unit Quantity": ["-"],
        "Additional Licenses": ["-"],
    })

    # Add numeric column totals
    for col in numeric_cols:
        if col in df.columns:
            total_row[col] = df[col].sum()

    # Remove any existing total row to prevent duplicates
    df = df[df["Cloud Service Description"] != "Total Services Cost"]

    # Concatenate the total row
    df = pd.concat([df, total_row], ignore_index=True)

    # Calculate the final totals for the PDF
    if 'Prepaid Co-Termed Cost' in df.columns:
        total_prepaid_cost = df.loc[df['Cloud Service Description'] != 'Total Services Cost', 'Prepaid Co-Termed Cost'].sum()
    if 'First Year Co-Termed Cost' in df.columns:
        total_first_year_cost = df.loc[df['Cloud Service Description'] != 'Total Services Cost', 'First Year Co-Termed Cost'].sum()
    if 'Updated Annual Cost' in df.columns:
        total_updated_annual_cost = df.loc[df['Cloud Service Description'] != 'Total Services Cost', 'Updated Annual Cost'].sum()
    if 'Subscription Term Total Service Fee' in df.columns:
        total_subscription_term_fee = df.loc[df['Cloud Service Description'] != 'Total Services Cost', 'Subscription Term Total Service Fee'].sum()

    return df, total_prepaid_cost, total_first_year_cost, total_updated_annual_cost, total_subscription_term_fee
def generate_pdf(customer_name, billing_term, months_remaining, extension_months, total_prepaid_cost, total_first_year_cost, total_updated_annual_cost, total_subscription_term_fee, data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 10)
    pdf.cell(200, 8, "Co-Terming Cost Report", ln=True, align="C")
    pdf.ln(4)
    
    pdf.set_font("Arial", "", 8)
    pdf.cell(200, 5, f"Date: {datetime.today().strftime('%Y-%m-%d')}", ln=True)
    pdf.cell(200, 5, f"Customer Name: {customer_name}", ln=True)
    pdf.cell(200, 5, f"Billing Term: {billing_term}", ln=True)
    pdf.cell(200, 5, f"Original Remaining Months: {months_remaining:.2f}", ln=True)
    if extension_months > 0:
        pdf.cell(200, 5, f"Extension Period: {extension_months} months", ln=True)
        pdf.cell(200, 5, f"Total Term: {months_remaining + extension_months:.2f} months", ln=True)
    pdf.cell(200, 5, f"Total Pre-Paid Cost: ${total_prepaid_cost:,.2f}", ln=True)
    pdf.cell(200, 5, f"First Year Co-Termed Cost: ${total_first_year_cost:,.2f}", ln=True)
    pdf.cell(200, 5, f"Updated Annual Cost: ${total_updated_annual_cost:,.2f}", ln=True)
    pdf.cell(200, 5, f"Subscription Term Total Service Fee: ${total_subscription_term_fee:,.2f}", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 7)
    pdf.cell(200, 5, "Detailed Line Items", ln=True)
    pdf.set_font("Arial", "", 5)
    
    headers = list(data.columns)
    col_widths = [35, 15, 20, 15, 25, 25, 25, 25, 25, 25]  # Adjust these widths as needed
    
    # Print headers
    for i, header in enumerate(headers):
        if i < len(col_widths):  # Only print if we have a defined width
            pdf.cell(col_widths[i], 4, header, border=1, align="C")
    pdf.ln()
    
    # Print data rows
    pdf.set_font("Arial", "", 5)
    for _, row in data.iterrows():
        for i, col in enumerate(headers):
            if i < len(col_widths):  # Only print if we have a defined width
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
# Add extension period option
add_extension = st.checkbox("Add Agreement Extension?")
if add_extension:
    extension_months = st.number_input("Extension Period (Months):", min_value=1, value=12, step=1, format="%d")
    total_term = months_remaining + extension_months
    st.info(f"Total Term: {total_term:.2f} months")
else:
    extension_months = 0
    total_term = months_remaining
num_items = st.number_input("Number of Line Items:", min_value=1, value=1, step=1, format="%d")

st.subheader("Enter License Information")
columns = ["Cloud Service Description", "Unit Quantity", "Annual Unit Fee", "Additional Licenses", "Prepaid Co-Termed Cost", "First Year Co-Termed Cost", "Updated Annual Cost", "Subscription Term Total Service Fee", "Monthly Co-Termed Cost", "First Month Co-Termed Cost"]
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
    data, total_prepaid_cost, total_first_year_cost, total_updated_annual_cost, total_subscription_term_fee = calculate_costs(
        data, 
        agreement_term, 
        months_remaining, 
        extension_months, 
        billing_term
    )
    
    st.subheader("Detailed Line Items")
    
    columns_to_drop = []
    if billing_term == 'Monthly':
        columns_to_drop = ['Prepaid Co-Termed Cost', 'First Year Co-Termed Cost', 'Updated Annual Cost']
        
        # Get the last row values (excluding the Total Services Cost row)
        mask = data['Cloud Service Description'] != 'Total Services Cost'
        total_monthly_co_termed = data[mask]['Monthly Co-Termed Cost'].iloc[-1]  # Get last row
        total_first_month = data[mask]['First Month Co-Termed Cost'].iloc[-1]  # Get last row
        
        # Convert to float and handle any currency formatting
        if isinstance(total_monthly_co_termed, str):
            total_monthly_co_termed = float(total_monthly_co_termed.replace('$', '').replace(',', ''))
        if isinstance(total_first_month, str):
            total_first_month = float(total_first_month.replace('$', '').replace(',', ''))
        
        st.write("Debug - Total Monthly Co-termed:", total_monthly_co_termed)
        st.write("Debug - Total First Month:", total_first_month)
        
        chart_data = {
            "coTermedMonthly": float(total_monthly_co_termed),  # Should be 250.00
            "newMonthly": float(total_first_month),            # Should be 137.50
            "subscription": float(total_subscription_term_fee)  # Looks correct at 12,581.25
        }
    elif billing_term == 'Annual':
        columns_to_drop = ['Prepaid Co-Termed Cost', 'Monthly Co-Termed Cost', 'First Month Co-Termed Cost']
        chart_data = {
            "firstYearCoTerm": float(total_first_year_cost),
            "newAnnual": float(total_updated_annual_cost),
            "subscription": float(total_subscription_term_fee)
        }
    elif billing_term == 'Prepaid':
        columns_to_drop = ['Monthly Co-Termed Cost', 'First Month Co-Termed Cost', 'First Year Co-Termed Cost', 'Updated Annual Cost']
        chart_data = {
            "coTermedPrepaid": float(total_prepaid_cost)
        }

    # Only drop columns that exist in the dataframe
    existing_columns_to_drop = [col for col in columns_to_drop if col in data.columns]
    if existing_columns_to_drop:
        data = data.drop(columns=existing_columns_to_drop)
        
    data = data.copy()
    for col in ["Annual Unit Fee", "Prepaid Co-Termed Cost", "Prepaid Additional Licenses Co-Termed Cost", 
                "First Year Co-Termed Cost", "Updated Annual Cost", "Subscription Term Total Service Fee", 
                "Monthly Co-Termed Cost", "First Month Co-Termed Cost"]:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors='coerce')
    
    st.dataframe(data.style.format({
        "Annual Unit Fee": "${:,.2f}",
        "Prepaid Co-Termed Cost": "${:,.2f}",
        "First Year Co-Termed Cost": "${:,.2f}",
        "Updated Annual Cost": "${:,.2f}",
        "Subscription Term Total Service Fee": "${:,.2f}",
        "Monthly Co-Termed Cost": "${:,.2f}",
        "First Month Co-Termed Cost": "${:,.2f}"
    }).set_properties(**{"white-space": "normal"}))
# Then in your "Calculate Costs" button section, after the dataframe display:
    st.write("### Cost Comparison")
    
    # Prepare different data based on billing term
    if billing_term == 'Prepaid':
        chart_data = {
            "coTermedPrepaid": float(total_prepaid_cost)
        }
    elif billing_term == 'Monthly':
        monthly_co_termed = float(data['Monthly Co-Termed Cost'].iloc[-2])  # Get the last non-total row
        first_month_co_termed = float(data['First Month Co-Termed Cost'].iloc[-2])  # Get the last non-total row
        chart_data = {
            "coTermedMonthly": monthly_co_termed,
            "newMonthly": first_month_co_termed,
            "subscription": float(total_subscription_term_fee)
        }
    else:  # Annual
        chart_data = {
            "firstYearCoTerm": float(total_first_year_cost),
            "newAnnual": float(total_updated_annual_cost),
            "subscription": float(total_subscription_term_fee)
        }
        st.write("Final chart_data being sent:", chart_data)

    components.html(
        CHART_HTML + f"""
        <script>
            renderChart({chart_data}, '{billing_term}');
        </script>
        """,
        height=500
    )
    # Now generate the PDF with all the calculated values
    pdf_path = generate_pdf(
        customer_name,
        billing_term,
        months_remaining,
        extension_months,
        total_prepaid_cost,
        total_first_year_cost,
        total_updated_annual_cost,
        total_subscription_term_fee,
        data
    )
    with open(pdf_path, "rb") as file:
        st.download_button(label="Download PDF", data=file, file_name="coterming_report.pdf", mime="application/pdf")
