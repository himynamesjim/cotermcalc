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
                            label: 'First Month Co-Termed Cost',  // Changed from 'Co-Termed Monthly Cost'
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
                }
             else if (billingTerm === 'Annual') {
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
                }
            else if (billingTerm === 'Prepaid') {
                    console.log('Prepaid data:', data);  // Debug log
                    datasets = [
                        {
                            label: 'Co-Termed Prepaid Cost',
                            data: [data.coTermedPrepaid || 0],
                            backgroundColor: '#8884d8'
                        },
                        {
                            label: 'Total Subscription Cost',
                            data: [data.subscription || 0],
                            backgroundColor: '#ffc658'
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
                    title: {
                        display: false  // Remove title padding
                    },
                    legend: {
                        position: 'top',
                        labels: {
                            padding: 15,  // Padding between legend items
                            font: {
                                size: 12  // Adjust font size if needed
                            }
                        },
                        margin: 0  // Remove extra margin
                    },
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
                        offset: 8
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
                layout: {
                    padding: {
                        top: 10,    // Reduced top padding
                        bottom: 10
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
def generate_pdf(customer_name, billing_term, months_remaining, extension_months, total_prepaid_cost, total_first_year_cost, total_updated_annual_cost, total_subscription_term_fee, data, agreement_term):
    pdf = FPDF()
    pdf.add_page()
    
    # Set column widths
    w_desc = 65  # Cloud Service Description
    w_qty = 25   # Unit Quantity
    w_fee = 25   # Annual Unit Fee
    w_lic = 25   # Additional Licenses
    w_cost = 30  # Cost column
    w_total = 30 # Total Service Fee

    # Agreement Information Section
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Agreement Information", ln=True, align="L")
    pdf.set_font("Arial", "", 10)
    
    # Left side of header
    pdf.cell(100, 6, f"Date: {datetime.today().strftime('%Y-%m-%d')}", ln=False)
    pdf.cell(0, 6, f"Agreement Term: {agreement_term:.2f} months", ln=True)
    
    pdf.cell(100, 6, f"Customer Name: {customer_name}", ln=False)
    pdf.cell(0, 6, f"Extension Period: {extension_months} months", ln=True)
    
    pdf.cell(100, 6, f"Billing Term: {billing_term}", ln=False)
    pdf.cell(0, 6, f"Total Term: {months_remaining + extension_months:.2f} months", ln=True)
    
    pdf.ln(10)  # Add some space
    
    # Cost Summary Section
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Cost Summary", ln=True, align="L")
    pdf.set_font("Arial", "", 10)
    
    # Dynamically adjust columns based on billing term
    if billing_term == 'Monthly':
        columns = [
            {'width': w_desc, 'title': 'Cloud Service Description', 'align': 'L'},
            {'width': w_qty, 'title': 'Unit Quantity', 'align': 'C'},
            {'width': w_fee, 'title': 'Annual Unit Fee', 'align': 'C'},
            {'width': w_lic, 'title': 'Additional Licenses', 'align': 'C'},
            {'width': w_cost, 'title': 'First Month Co-Termed Cost', 'align': 'C'},
            {'width': w_total, 'title': 'Subscription Term Total Service Fee', 'align': 'C'}
        ]
    elif billing_term == 'Annual':
        columns = [
            {'width': w_desc, 'title': 'Cloud Service Description', 'align': 'L'},
            {'width': w_qty, 'title': 'Unit Quantity', 'align': 'C'},
            {'width': w_fee, 'title': 'Annual Unit Fee', 'align': 'C'},
            {'width': w_lic, 'title': 'Additional Licenses', 'align': 'C'},
            {'width': w_cost, 'title': 'First Year Co-Termed Cost', 'align': 'C'},
            {'width': w_total, 'title': 'Subscription Term Total Service Fee', 'align': 'C'}
        ]
    else:  # Prepaid
        columns = [
            {'width': w_desc, 'title': 'Cloud Service Description', 'align': 'L'},
            {'width': w_qty, 'title': 'Unit Quantity', 'align': 'C'},
            {'width': w_fee, 'title': 'Annual Unit Fee', 'align': 'C'},
            {'width': w_lic, 'title': 'Additional Licenses', 'align': 'C'},
            {'width': w_cost, 'title': 'Prepaid Co-Termed Cost', 'align': 'C'},
            {'width': w_total, 'title': 'Subscription Term Total Service Fee', 'align': 'C'}
        ]
    
    # Dynamically adjust cost summary based on billing term
    if billing_term == 'Monthly':
        # Find the first month co-termed cost from the Total Services Cost row
        total_row = data[data['Cloud Service Description'] == 'Total Services Cost']
        first_month_co_termed = float(total_row['First Month Co-Termed Cost'].iloc[0])
        
        first_cost_label = "First Month Co-Termed Cost"
        first_cost_value = first_month_co_termed
        second_cost_label = "Subscription Term Total"
        second_cost_value = total_subscription_term_fee
    elif billing_term == 'Annual':
        first_cost_label = "First Year Co-Termed Cost"
        first_cost_value = total_first_year_cost
        second_cost_label = "Updated Annual Cost"
        second_cost_value = total_updated_annual_cost
        third_cost_label = "Subscription Term Total"
        third_cost_value = total_subscription_term_fee
    else:  # Prepaid
        first_cost_label = "Total Pre-Paid Cost"
        first_cost_value = total_prepaid_cost
        second_cost_label = "Subscription Term Total"
        second_cost_value = total_subscription_term_fee
    
    # Left side of cost summary
    pdf.cell(100, 6, f"{first_cost_label}: ${first_cost_value:,.2f}", ln=False)
    pdf.cell(0, 6, f"{second_cost_label}: ${second_cost_value:,.2f}", ln=True)
    
    # For Annual billing, add Subscription Term Total
    if billing_term == 'Annual':
        pdf.cell(100, 6, "", ln=False)  # Empty left column
        pdf.cell(0, 6, f"{third_cost_label}: ${third_cost_value:,.2f}", ln=True)
    
    # For Monthly and Prepaid, show updated annual cost if non-zero
    if billing_term in ['Monthly', 'Prepaid'] and total_updated_annual_cost > 0:
        pdf.cell(100, 6, "Updated Annual Cost: $0.00", ln=False)
        pdf.cell(0, 6, f"Updated Annual Cost: ${total_updated_annual_cost:,.2f}", ln=True)
    
    pdf.ln(10)
    
    # Detailed Line Items
    pdf.set_font("Arial", "B", 7)
    pdf.cell(200, 5, "Detailed Line Items", ln=True)

    # Print headers
    pdf.set_font("Arial", "B", 7)
    
    # Single row with multi-line headers
    def print_multiline_header(pdf, width, lines, border=1, align='C'):
        # Store current position
        x = pdf.get_x()
        y = pdf.get_y()
        
        # Calculate max height needed
        max_height = 6  # Base height
        
        # Print each line
        for i, line in enumerate(lines):
            pdf.set_xy(x, y + (i * 3))  # Slight vertical offset between lines
            pdf.cell(width, 3, line, border=(border if i == len(lines)-1 else 0), align=align)
        
        # Move to next column
        pdf.set_xy(x + width, y)
    
    # Prepare multi-line headers
    headers = [
        ['Cloud Service\nDescription'],
        ['Unit\nQuantity'],
        ['Annual\nUnit Fee'],
        ['Additional\nLicenses'],
        ['First Year\nCo-Termed\nCost'],
        ['Subscription Term\nTotal\nService Fee']
    ]
    
    # Print headers
    for header in headers:
        print_multiline_header(pdf, w_desc if header[0] == 'Cloud Service\nDescription' else w_qty, header[0])
    
    # Move to next line
    pdf.ln(6)

    # Print data
    pdf.set_font("Arial", "", 7)
    for _, row in data.iterrows():
        if row['Cloud Service Description'] == 'Total Services Cost':
            pdf.set_font("Arial", "B", 7)
        
        pdf.cell(w_desc, 6, str(row['Cloud Service Description']), 1, 0, 'L')
        pdf.cell(w_qty, 6, str(row['Unit Quantity']), 1, 0, 'C')
        pdf.cell(w_fee, 6, f"${float(row['Annual Unit Fee']):,.2f}", 1, 0, 'R')
        pdf.cell(w_lic, 6, str(row['Additional Licenses']), 1, 0, 'C')
        
        # Dynamically select the appropriate cost column
        if billing_term == 'Monthly':
            cost_value = row.get('First Month Co-Termed Cost', 0)
        elif billing_term == 'Annual':
            cost_value = row.get('First Year Co-Termed Cost', 0)
        else:  # Prepaid
            cost_value = row.get('Prepaid Co-Termed Cost', 0)
        
        pdf.cell(w_cost, 6, f"${float(cost_value):,.2f}", 1, 0, 'R')
        pdf.cell(w_total, 6, f"${float(row['Subscription Term Total Service Fee']):,.2f}", 1, 1, 'R')
        
        pdf.set_font("Arial", "", 7)

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
    
   # Handle column dropping first
    columns_to_drop = []
    if billing_term == 'Monthly':
        columns_to_drop = ['Prepaid Co-Termed Cost', 'First Year Co-Termed Cost', 'Updated Annual Cost']
    elif billing_term == 'Annual':
        columns_to_drop = ['Prepaid Co-Termed Cost', 'Monthly Co-Termed Cost', 'First Month Co-Termed Cost']
    elif billing_term == 'Prepaid':
        columns_to_drop = ['Monthly Co-Termed Cost', 'First Month Co-Termed Cost', 'First Year Co-Termed Cost', 'Updated Annual Cost']

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

    st.write("### Cost Comparison")
    
    # Prepare chart data based on billing term
    if billing_term == 'Monthly':
        # Get values from the Total Services Cost row
        total_row = data[data['Cloud Service Description'] == 'Total Services Cost']
        monthly_co_termed = float(total_row['Monthly Co-Termed Cost'].iloc[0])      # Will be 250.00
        first_month_co_termed = float(total_row['First Month Co-Termed Cost'].iloc[0])  # Will be 137.50
        
        chart_data = {
            "coTermedMonthly": first_month_co_termed,  # This will be 137.50
            "newMonthly": monthly_co_termed,           # This will be 250.00
            "subscription": float(total_subscription_term_fee)
        }
    elif billing_term == 'Annual':
        chart_data = {
            "firstYearCoTerm": float(total_first_year_cost),
            "newAnnual": float(total_updated_annual_cost),
            "subscription": float(total_subscription_term_fee)
        }
    elif billing_term == 'Prepaid':
        chart_data = {
            "coTermedPrepaid": float(total_prepaid_cost),
            "subscription": float(total_subscription_term_fee)  # Added this line
        }
    
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
        data,
        agreement_term  # Add this parameter
    )
    with open(pdf_path, "rb") as file:
        st.download_button(label="Download PDF", data=file, file_name="coterming_report.pdf", mime="application/pdf")
