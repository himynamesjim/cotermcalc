import streamlit as st
import pandas as pd
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from fpdf import FPDF
import streamlit.components.v1 as components
import base64
import io
import os

# Set page configuration and theme options
st.set_page_config(
    page_title="Co-Terming Cost Calculator",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables if they don't exist
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'
    
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 'calculator'

# For tab navigation
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = 0

# Custom CSS for styling
def local_css():
    # Define CSS based on current theme
    if st.session_state.theme == 'dark':
        bg_color = "#0e1117"
        text_color = "#ffffff"
        accent_color = "#4b8bbe"
        secondary_bg = "#262730"
    else:
        bg_color = "#ffffff"
        text_color = "#31333F"
        accent_color = "#2E86C1"
        secondary_bg = "#f0f2f6"
    
    return f"""
    <style>
    .main-header {{
        font-size: 2.5rem;
        font-weight: 600;
        color: {text_color};
        margin-bottom: 1rem;
        text-align: center;
        background-color: {secondary_bg};
        padding: 1rem;
        border-radius: 0.5rem;
    }}
    .sub-header {{
        font-size: 1.5rem;
        font-weight: 500;
        color: {accent_color};
        margin: 1rem 0;
        padding-top: 1rem;
        border-top: 1px solid {secondary_bg};
    }}
    .info-box {{
        background-color: {secondary_bg};
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }}
    .highlight {{
        color: {accent_color};
        font-weight: bold;
    }}
    .customer-section {{
        background-color: {secondary_bg};
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
    }}
    .email-template {{
        background-color: {secondary_bg};
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
        white-space: pre-wrap;
        font-family: monospace;
    }}
    .footer {{
        margin-top: 3rem;
        text-align: center;
        color: gray;
        font-size: 0.8rem;
    }}
    .navigation-buttons {{
        display: flex;
        justify-content: space-between;
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid {secondary_bg};
    }}
    </style>
    """

# Function to navigate between tabs
def change_tab(tab_index):
    st.session_state.current_tab = tab_index

# Apply CSS
st.markdown(local_css(), unsafe_allow_html=True)

# Chart HTML/JS with dynamic theme support
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
        
        function renderChart(data, billingTerm, theme) {
            const ctx = document.getElementById('costChart').getContext('2d');
            
            // Theme colors
            const colors = theme === 'dark' ? {
                backgroundColor: '#1e1e1e',
                textColor: '#ffffff',
                gridColor: 'rgba(255, 255, 255, 0.1)',
                barColors: ['#8884d8', '#82ca9d', '#ffc658']
            } : {
                backgroundColor: '#ffffff',
                textColor: '#31333F',
                gridColor: 'rgba(0, 0, 0, 0.1)',
                barColors: ['#8884d8', '#82ca9d', '#ffc658']
            };
            
            // Define datasets based on billing term
            let datasets = [];
            
            if (billingTerm === 'Monthly') {
                datasets = [
                    {
                        label: 'Current Monthly Cost',
                        data: [data.currentCost || 0],
                        backgroundColor: colors.barColors[0]
                    },
                    {
                        label: 'First Month Co-Termed Cost',
                        data: [data.coTermedMonthly || 0],
                        backgroundColor: colors.barColors[1]
                    },
                    {
                        label: 'Subscription Term Total',
                        data: [data.subscription || 0],
                        backgroundColor: colors.barColors[2]
                    }
                ];
            }
            else if (billingTerm === 'Annual') {
                datasets = [
                    {
                        label: 'Current Annual Cost',
                        data: [data.currentCost || 0],
                        backgroundColor: colors.barColors[0]
                    },
                    {
                        label: 'First Year Co-Termed Cost',
                        data: [data.firstYearCoTerm || 0],
                        backgroundColor: colors.barColors[1]
                    },
                    {
                        label: 'Updated Annual Cost',
                        data: [data.newAnnual || 0],
                        backgroundColor: colors.barColors[2]
                    }
                ];
            }
            else if (billingTerm === 'Prepaid') {
                datasets = [
                    {
                        label: 'Current Annual Cost',
                        data: [data.currentCost || 0],
                        backgroundColor: colors.barColors[0]
                    },
                    {
                        label: 'Co-Termed Prepaid Cost',
                        data: [data.coTermedPrepaid || 0],
                        backgroundColor: colors.barColors[1]
                    },
                    {
                        label: 'Total Subscription Cost',
                        data: [data.subscription || 0],
                        backgroundColor: colors.barColors[2]
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
                            display: false
                        },
                        legend: {
                            position: 'top',
                            labels: {
                                padding: 15,
                                font: {
                                    size: 12
                                },
                                color: colors.textColor
                            },
                            margin: 0
                        },
                        datalabels: {
                            anchor: 'end',
                            align: 'top',
                            formatter: function(value) {
                                return '

def calculate_costs(df, agreement_term, months_remaining, extension_months, billing_term):
    total_term = months_remaining + extension_months
    months_elapsed = agreement_term - months_remaining
    total_prepaid_cost = 0
    total_first_year_cost = 0
    total_updated_annual_cost = 0
    total_subscription_term_fee = 0
    total_current_cost = 0  # Current cost before additional licenses

    for index, row in df.iterrows():
        # Calculate current costs (before additional licenses)
        current_monthly_cost = (row['Annual Unit Fee'] / 12) * row['Unit Quantity']
        current_annual_cost = row['Unit Quantity'] * row['Annual Unit Fee']
        
        # Calculate costs with additional licenses
        first_month_co_termed_cost = (row['Annual Unit Fee'] / 12) * row['Additional Licenses'] * (months_remaining % 1) if billing_term == 'Monthly' else 0
        monthly_co_termed_cost = (row['Annual Unit Fee'] / 12) * row['Additional Licenses'] if billing_term == 'Monthly' else 0
        annual_total_fee = row['Unit Quantity'] * row['Annual Unit Fee']
        subscription_term_total_fee = ((annual_total_fee * total_term) / 12) + ((row['Additional Licenses'] * row['Annual Unit Fee'] * total_term) / 12)
        co_termed_prepaid_cost = (row['Additional Licenses'] * row['Annual Unit Fee'] * total_term) / 12 if billing_term == 'Prepaid' else 0
        co_termed_first_year_cost = (row['Additional Licenses'] * row['Annual Unit Fee'] * (12 - (months_elapsed % 12))) / 12 if billing_term == 'Annual' else 0
        updated_annual_cost = annual_total_fee + (row['Additional Licenses'] * row['Annual Unit Fee']) if billing_term == 'Annual' else 0

        # Store calculated values in the dataframe based on billing term
        if billing_term == 'Monthly':
            df.at[index, 'Current Monthly Cost'] = current_monthly_cost
            df.at[index, 'First Month Co-Termed Cost'] = first_month_co_termed_cost
            df.at[index, 'Monthly Co-Termed Cost'] = monthly_co_termed_cost
        elif billing_term == 'Annual':
            df.at[index, 'Current Annual Cost'] = current_annual_cost
            df.at[index, 'First Year Co-Termed Cost'] = co_termed_first_year_cost
            df.at[index, 'Updated Annual Cost'] = updated_annual_cost
        else:  # Prepaid
            df.at[index, 'Current Annual Cost'] = current_annual_cost
            df.at[index, 'Prepaid Co-Termed Cost'] = co_termed_prepaid_cost
            
        # Always add the subscription term total
        df.at[index, 'Subscription Term Total Service Fee'] = subscription_term_total_fee

    # Convert numeric columns to float - only convert columns that exist
    numeric_cols = [
        "Annual Unit Fee", "Current Monthly Cost", "Current Annual Cost", "Prepaid Co-Termed Cost",
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
    if 'Current Annual Cost' in df.columns:
        total_current_cost = df.loc[df['Cloud Service Description'] != 'Total Services Cost', 'Current Annual Cost'].sum()
    if 'Prepaid Co-Termed Cost' in df.columns:
        total_prepaid_cost = df.loc[df['Cloud Service Description'] != 'Total Services Cost', 'Prepaid Co-Termed Cost'].sum()
    if 'First Year Co-Termed Cost' in df.columns:
        total_first_year_cost = df.loc[df['Cloud Service Description'] != 'Total Services Cost', 'First Year Co-Termed Cost'].sum()
    if 'Updated Annual Cost' in df.columns:
        total_updated_annual_cost = df.loc[df['Cloud Service Description'] != 'Total Services Cost', 'Updated Annual Cost'].sum()
    if 'Subscription Term Total Service Fee' in df.columns:
        total_subscription_term_fee = df.loc[df['Cloud Service Description'] != 'Total Services Cost', 'Subscription Term Total Service Fee'].sum()

    return df, total_current_cost, total_prepaid_cost, total_first_year_cost, total_updated_annual_cost, total_subscription_term_fee

def generate_pdf(billing_term, months_remaining, extension_months, total_current_cost, total_prepaid_cost, 
                total_first_year_cost, total_updated_annual_cost, total_subscription_term_fee, data, agreement_term, 
                customer_name="", customer_email="", account_manager="", company_name="", logo_path=None):
    pdf = FPDF(orientation='L')
    pdf.add_page()
    pdf.set_font("Arial", "B", 10)
    
    # Add logo if provided
    if logo_path and os.path.exists(logo_path):
        try:
            pdf.image(logo_path, x=10, y=10, w=50)
        except Exception as e:
            print(f"Could not add logo: {e}")
    
    # Add title
    pdf.cell(280, 8, "Co-Terming Cost Report", ln=True, align="C")
    pdf.ln(4)
    
    # Move content down to make room for logo if needed
    pdf.set_y(50)
    
    # Adjust column widths for landscape
    w_desc = 75
    w_qty = 30
    w_fee = 30
    w_lic = 30
    w_cost = 40
    w_total = 60

    # Customer Information Section
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Customer Information", ln=True, align="L")
    pdf.set_font("Arial", "", 10)
    
    pdf.cell(100, 6, f"Customer: {customer_name}", ln=False)
    pdf.cell(0, 6, f"Contact Email: {customer_email}", ln=True)
    
    pdf.cell(100, 6, f"Account Manager: {account_manager}", ln=False)
    pdf.cell(0, 6, f"Company: {company_name}", ln=True)
    
    pdf.ln(5)
    
    # Agreement Information Section
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Agreement Information", ln=True, align="L")
    pdf.set_font("Arial", "", 10)
    
    # Left side of header
    pdf.cell(100, 6, f"Date: {datetime.today().strftime('%Y-%m-%d')}", ln=False)
    pdf.cell(0, 6, f"Agreement Term: {agreement_term:.2f} months", ln=True)
    
    pdf.cell(0, 6, f"Extension Period: {extension_months} months", ln=True)
    
    pdf.cell(100, 6, f"Billing Term: {billing_term}", ln=False)
    pdf.cell(0, 6, f"Total Term: {months_remaining + extension_months:.2f} months", ln=True)
    
    pdf.ln(10)
    
    # Cost Summary Section
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Cost Summary", ln=True, align="L")
    pdf.set_font("Arial", "", 10)
    
    # Add current cost information
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 6, f"Current Annual Cost (Before Additional Licenses): ${total_current_cost:,.2f}", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.ln(5)
    
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
        pdf.cell(100, 6, "", ln=False)  # Empty left column
        pdf.cell(0, 6, f"Updated Annual Cost: ${total_updated_annual_cost:,.2f}", ln=True)
    
    pdf.ln(10)
    
    # Detailed Line Items
    pdf.set_font("Arial", "B", 7)
    pdf.cell(200, 5, "Detailed Line Items", ln=True)
    
    # Print headers
    pdf.set_font("Arial", "B", 7)
    
    # Print headers in a single row using cell method
    pdf.cell(w_desc, 6, 'Cloud Service Description', 1, 0, 'C')
    pdf.cell(w_qty, 6, 'Unit Quantity', 1, 0, 'C')
    pdf.cell(w_fee, 6, 'Annual Unit Fee', 1, 0, 'C')
    pdf.cell(w_lic, 6, 'Additional Licenses', 1, 0, 'C')
    pdf.cell(w_cost, 6, columns[-2]['title'], 1, 0, 'C')
    pdf.cell(w_total, 6, columns[-1]['title'], 1, 1, 'C')
    
    # Add a small line break
    pdf.ln(1)

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
    
    # Add footer with company information
    pdf.ln(10)
    pdf.set_font("Arial", "I", 8)
    pdf.cell(0, 6, f"Generated by {company_name}", 0, 0, 'C')

    pdf_buffer = io.BytesIO()
    pdf.output(pdf_buffer)
    pdf_buffer.seek(0)
    
    return pdf_buffer

def generate_email_template(billing_term, customer_name, current_cost, first_cost, total_subscription_cost, company_name, account_manager, updated_annual_cost=0):
    # Format currency values
    current_cost_str = "${:,.2f}".format(current_cost)
    first_cost_str = "${:,.2f}".format(first_cost)
    total_subscription_cost_str = "${:,.2f}".format(total_subscription_cost)
    updated_annual_cost_str = "${:,.2f}".format(updated_annual_cost)
    
    # Common parts
    greeting = "Dear " + str(customer_name) + ",\n\n"
    footer = "\nWe appreciate your continued business and look forward to your approval.\n\nBest regards,\n" + str(account_manager) + "\n" + str(company_name) + " Sales Team"
    next_steps = "\nNext Steps:\n1. Please carefully review the cost breakdown above.\n2. If you approve these terms, kindly reply to this email with your confirmation.\n3. If you have any questions or concerns, please contact our sales team."
    
    if billing_term == 'Monthly':
        body = "We are writing to inform you about the updated co-terming cost for your monthly billing arrangement.\n\n"
        body += "Current Agreement:\n- Current Annual Cost: " + current_cost_str + "\n\n"
        body += "Updated Cost Summary:\n- First Month Co-Termed Cost: " + first_cost_str + "\n"
        body += "- Total Subscription Cost: " + total_subscription_cost_str + "\n"
        
        if updated_annual_cost > 0:
            body += "- Updated Annual Cost: " + updated_annual_cost_str + "\n"
        
        body += "\nKey Details:\n- The first month's co-termed cost reflects your current service adjustments.\n"
        body += "- Your total subscription cost covers the entire term of the agreement."
        
    elif billing_term == 'Annual':
        body = "We are writing to inform you about the updated co-terming cost for your annual billing arrangement.\n\n"
        body += "Current Agreement:\n- Current Annual Cost: " + current_cost_str + "\n\n"
        body += "Updated Cost Summary:\n- First Year Co-Termed Cost: " + first_cost_str + "\n"
        body += "- Updated Annual Cost: " + updated_annual_cost_str + "\n"
        body += "- Total Subscription Cost: " + total_subscription_cost_str + "\n"
        
        body += "\nKey Details:\n- The first year's co-termed cost reflects your current service adjustments.\n"
        body += "- Your total subscription cost covers the entire term of the agreement."
        
    elif billing_term == 'Prepaid':
        body = "We are writing to inform you about the updated co-terming cost for your prepaid billing arrangement.\n\n"
        body += "Current Agreement:\n- Current Annual Cost: " + current_cost_str + "\n\n"
        body += "Updated Cost Summary:\n- Total Pre-Paid Cost: " + first_cost_str + "\n"
        body += "- Total Subscription Cost: " + total_subscription_cost_str + "\n"
        
        if updated_annual_cost > 0:
            body += "- Updated Annual Cost: " + updated_annual_cost_str + "\n"
        
        body += "\nKey Details:\n- The pre-paid cost covers your entire service term.\n"
        body += "- Your total subscription cost reflects the full agreement period."
    
    else:
        return "Invalid billing term"
    
    # Combine all parts
    complete_template = greeting + body + next_steps + footer
    return complete_template

def copy_to_clipboard_button(text, button_text="Copy to Clipboard"):
    # Create a unique key for this button
    button_id = f"copy_button_{hash(text)}"
    
    # JavaScript function to copy text to clipboard
    js_code = f"""
    <script>
    function copyToClipboard_{button_id}() {{
        const el = document.createElement('textarea');
        el.value = `{text.replace('`', '\\`')}`;
        document.body.appendChild(el);
        el.select();
        document.execCommand('copy');
        document.body.removeChild(el);
        
        // Change button text temporarily
        const btn = document.getElementById('{button_id}');
        const originalText = btn.innerHTML;
        btn.innerHTML = 'Copied!';
        setTimeout(() => {{
            btn.innerHTML = originalText;
        }}, 2000);
    }}
    </script>
    """
    
# Alternative approach - put everything on one line
html_button = f"""{js_code}<button id='{button_id}' onclick='copyToClipboard_{button_id}()' style='background-color: #4CAF50; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; margin-top: 10px;'>{button_text}</button>"""
    
    return html_button

# Navigation function remains for potential future use
# No navigation buttons

# Sidebar for navigation and settings
with st.sidebar:
    st.image("https://via.placeholder.com/150x50.png?text=Your+Logo", width=150)
    st.title("Navigation")
    
    # Navigation menu
    nav_options = ["Calculator", "Help & Documentation", "About"]
    nav_selection = st.radio("Go to:", nav_options)
    
    # Set the active tab based on navigation selection
    st.session_state.active_tab = nav_selection.lower().replace(" & ", "_").replace(" ", "_")
    
    st.markdown("---")
    
    # Theme toggle
    st.subheader("Settings")
    theme_options = ["Light", "Dark"]
    selected_theme = st.radio("Theme:", theme_options, index=0 if st.session_state.theme == 'light' else 1)
    st.session_state.theme = selected_theme.lower()
    
    st.markdown("---")
    
    # Uploader for logo
    st.subheader("Company Logo")
    uploaded_logo = st.file_uploader("Upload your logo for PDF reports", type=["png", "jpg", "jpeg"])
    if uploaded_logo:
        # Save the uploaded file
        logo_path = "logo.png"
        with open(logo_path, "wb") as f:
            f.write(uploaded_logo.getbuffer())
        st.success("Logo uploaded successfully!")
    else:
        logo_path = None
    
    st.markdown("---")
    
    # App info
    st.markdown("##### Co-Terming Calculator v1.1")
    st.markdown("© 2024 Your Company")

# Main content area
if st.session_state.active_tab in ['calculator', 'results']:
    # Custom HTML header
    st.markdown('<div class="main-header">Co-Terming Cost Calculator</div>', unsafe_allow_html=True)
    
    # Create tabs for different sections of the calculator
    tab_titles = ["Agreement Info", "Customer Info", "Services", "Results", "Email Template"]
    
    # Set the active tab based on session state
    active_tab_index = st.session_state.current_tab
    tabs = st.tabs(tab_titles)
    
    with tabs[0]:
        st.markdown('<div class="sub-header">Agreement Information</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            current_date = datetime.today().strftime('%Y-%m-%d')
            st.text(f"Current Date: {current_date}")
            billing_term = st.selectbox("Billing Term:", ["Annual", "Prepaid", "Monthly"])
            # Add date picker for agreement start date
            agreement_start_date = st.date_input("Agreement Start Date:", 
                                               value=date.today() - relativedelta(months=6),
                                               max_value=date.today())
        
        with col2:
            agreement_term = st.number_input("Agreement Term (Months):", min_value=1, value=36, step=1, format="%d")
            
            # Calculate months remaining based on start date and agreement term with day precision
            today = date.today()
            
            # Calculate full months passed
            months_passed = relativedelta(today, agreement_start_date).years * 12 + relativedelta(today, agreement_start_date).months
            
            # Calculate the day fraction of the current month
            # Get days in the current month
            if today.month == 12:
                last_day_of_month = date(today.year + 1, 1, 1) - relativedelta(days=1)
            else:
                last_day_of_month = date(today.year, today.month + 1, 1) - relativedelta(days=1)
            
            days_in_month = last_day_of_month.day
            day_fraction = (days_in_month - today.day) / days_in_month
            
            # Add the day fraction to get precise months passed
            precise_months_passed = months_passed + (1 - day_fraction)
            
            # Calculate remaining months with precision
            calculated_months_remaining = max(0, agreement_term - precise_months_passed)
            
            # Display calculated months remaining with 2 decimal precision
            st.text(f"Calculated Months Remaining: {calculated_months_remaining:.2f}")
            
            # Allow manual override of months remaining
            months_remaining = st.number_input("Override Months Remaining (if needed):", 
                                             min_value=0.0, 
                                             max_value=float(agreement_term), 
                                             value=float(calculated_months_remaining), 
                                             step=0.01, 
                                             format="%.2f")
        
        # Add extension period option
        add_extension = st.checkbox("Add Agreement Extension?")
        if add_extension:
            extension_months = st.number_input("Extension Period (Months):", min_value=1, value=12, step=1, format="%d")
            total_term = months_remaining + extension_months
            st.info(f"Total Term: {total_term:.2f} months")
        else:
            extension_months = 0
            total_term = months_remaining
        
        # No navigation buttons
            
    with tabs[1]:
        st.markdown('<div class="sub-header">Customer Information</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            customer_name = st.text_input("Customer Name:", placeholder="Enter customer name")
            customer_email = st.text_input("Customer Email:", placeholder="Enter customer email")
        
        with col2:
            account_manager = st.text_input("Account Manager:", placeholder="Enter account manager name")
            company_name = st.text_input("Your Company:", value="Your Company Name", placeholder="Enter your company name")
        
        # No navigation buttons
            
    with tabs[2]:
        st.markdown('<div class="sub-header">Service Information</div>', unsafe_allow_html=True)
        
        num_items = st.number_input("Number of Line Items:", min_value=1, value=1, step=1, format="%d")
        
        columns = ["Cloud Service Description", "Unit Quantity", "Annual Unit Fee", "Additional Licenses", 
                  "Prepaid Co-Termed Cost", "First Year Co-Termed Cost", "Updated Annual Cost", 
                  "Subscription Term Total Service Fee", "Monthly Co-Termed Cost", "First Month Co-Termed Cost"]
        data = pd.DataFrame(columns=columns)
        
        # Define numeric columns for proper handling
        numeric_cols = [
            "Annual Unit Fee", "Current Monthly Cost", "Current Annual Cost", "Prepaid Co-Termed Cost",
            "First Year Co-Termed Cost", "Updated Annual Cost", "Subscription Term Total Service Fee",
            "Monthly Co-Termed Cost", "First Month Co-Termed Cost"
        ]
        
        # Create a container for the line items
        line_items_container = st.container()
        
        with line_items_container:
            for i in range(num_items):
                st.markdown(f"**Item {i+1}**")
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                
                # Use a unique key for each input to avoid conflicts
                service_key = f"service_{i}"
                qty_key = f"qty_{i}"
                fee_key = f"fee_{i}"
                add_lic_key = f"add_lic_{i}"
                
                        # Create input fields for each row
                service = col1.text_input("Service Description", key=service_key, placeholder="Enter service name")
                qty = col2.number_input("Quantity", min_value=0, value=1, step=1, format="%d", key=qty_key)
                fee = col3.number_input("Annual Fee ($)", min_value=0.0, value=1000.0, step=100.0, format="%.2f", key=fee_key)
                add_lic = col4.number_input("Add. Licenses", min_value=0, value=0, step=1, format="%d", key=add_lic_key)
                
                # Add the row data to our dataframe
                row_data = {
                    "Cloud Service Description": service if service else "",
                    "Unit Quantity": qty,
                    "Annual Unit Fee": fee,
                    "Additional Licenses": add_lic,
                }
                
                # Fill in missing columns with empty values or zeros
                for col in columns:
                    if col not in row_data:
                        row_data[col] = 0 if col in numeric_cols else ""
                        
                # Append to the dataframe
                new_row = pd.DataFrame([row_data])
                data = pd.concat([data, new_row], ignore_index=True)
        
        # Add validation for empty service descriptions
        empty_services = data["Cloud Service Description"].isnull() | (data["Cloud Service Description"] == "")
        if empty_services.any():
            st.warning("⚠️ Please enter a description for all services.")
        
        # Store service data in session state
        st.session_state.service_data = data
        
        # No navigation buttons
            
    with tabs[3]:
        st.markdown('<div class="sub-header">Results</div>', unsafe_allow_html=True)
        
        # Check if we have service data in session state from the Services tab
        if 'service_data' in st.session_state:
            data = st.session_state.service_data
            valid_data = True
        else:
            # Check if we have valid data before calculating
            valid_data = not empty_services.any() and len(data) > 0
        
        # Create a placeholder for calculation results
        results_placeholder = st.empty()
        
        # Calculate button on the results page
        calculate_button = st.button("Calculate Costs", disabled=not valid_data, 
                                     help="Enter all required information to enable calculations")
        
        # Store calculation results in session state
        if "calculation_results" not in st.session_state:
            st.session_state.calculation_results = None
            
        if calculate_button and valid_data:
            with st.spinner("Calculating costs..."):
                # Calculate costs
                processed_data, total_current_cost, total_prepaid_cost, total_first_year_cost, total_updated_annual_cost, total_subscription_term_fee = calculate_costs(
                    data,
                    agreement_term,
                    months_remaining,
                    extension_months,
                    billing_term
                )
                
                # Store results in session state
                st.session_state.calculation_results = {
                    "processed_data": processed_data,
                    "total_current_cost": total_current_cost,
                    "total_prepaid_cost": total_prepaid_cost,
                    "total_first_year_cost": total_first_year_cost,
                    "total_updated_annual_cost": total_updated_annual_cost,
                    "total_subscription_term_fee": total_subscription_term_fee
                }
                
            st.success("Calculations completed successfully!")
            
        # Display results if available
        if st.session_state.calculation_results:
            results = st.session_state.calculation_results
            processed_data = results["processed_data"]
            total_current_cost = results["total_current_cost"]
            total_prepaid_cost = results["total_prepaid_cost"]
            total_first_year_cost = results["total_first_year_cost"]
            total_updated_annual_cost = results["total_updated_annual_cost"]
            total_subscription_term_fee = results["total_subscription_term_fee"]
            
            with results_placeholder.container():
                st.subheader("Detailed Line Items")
                
                # Handle column dropping more thoroughly
                columns_to_drop = []
                if billing_term == 'Monthly':
                    columns_to_drop = ['Prepaid Co-Termed Cost', 'First Year Co-Termed Cost', 'Updated Annual Cost', 'Current Annual Cost']
                elif billing_term == 'Annual':
                    columns_to_drop = ['Prepaid Co-Termed Cost', 'Monthly Co-Termed Cost', 'First Month Co-Termed Cost', 'Current Monthly Cost']
                elif billing_term == 'Prepaid':
                    columns_to_drop = ['Monthly Co-Termed Cost', 'First Month Co-Termed Cost', 'First Year Co-Termed Cost', 'Updated Annual Cost', 'Current Monthly Cost']
                
                # Only drop columns that exist in the dataframe
                displayed_data = processed_data.copy()
                existing_columns_to_drop = [col for col in columns_to_drop if col in displayed_data.columns]
                if existing_columns_to_drop:
                    displayed_data = displayed_data.drop(columns=existing_columns_to_drop)
                
                # Format numeric columns
                for col in ["Annual Unit Fee", "Prepaid Co-Termed Cost", "First Year Co-Termed Cost", 
                            "Updated Annual Cost", "Subscription Term Total Service Fee", 
                            "Monthly Co-Termed Cost", "First Month Co-Termed Cost"]:
                    if col in displayed_data.columns:
                        displayed_data[col] = pd.to_numeric(displayed_data[col], errors='coerce')
                
                # Display the dataframe with formatting
                st.dataframe(displayed_data.style.format({
                    "Annual Unit Fee": "${:,.2f}",
                    "Prepaid Co-Termed Cost": "${:,.2f}",
                    "First Year Co-Termed Cost": "${:,.2f}",
                    "Updated Annual Cost": "${:,.2f}",
                    "Subscription Term Total Service Fee": "${:,.2f}",
                    "Monthly Co-Termed Cost": "${:,.2f}",
                    "First Month Co-Termed Cost": "${:,.2f}"
                }).set_properties(**{"white-space": "normal"}))
                
                # Show current cost summary based on billing term
                st.markdown("### Current Agreement Cost")
                
                if billing_term == 'Monthly':
                    # Show only monthly cost for Monthly billing term
                    current_monthly = total_current_cost / 12
                    st.markdown(f"**Current Monthly Cost:** ${current_monthly:,.2f}")
                else:
                    # Show only annual cost for Annual and Prepaid billing terms
                    st.markdown(f"**Current Annual Cost:** ${total_current_cost:,.2f}")
                
                # Calculate total licenses (current + additional)
                total_current_licenses = processed_data[processed_data['Cloud Service Description'] != 'Total Services Cost']['Unit Quantity'].sum()
                total_additional_licenses = processed_data[processed_data['Cloud Service Description'] != 'Total Services Cost']['Additional Licenses'].sum()
                total_licenses = total_current_licenses + total_additional_licenses
                
                # Display license summary
                st.markdown("### License Summary")
                license_data = {
                    "License Type": ["Current Licenses", "Additional Licenses", "Total Licenses"],
                    "Count": [
                        f"{int(total_current_licenses)}",
                        f"{int(total_additional_licenses)}",
                        f"{int(total_licenses)}"
                    ]
                }
                
                license_df = pd.DataFrame(license_data)
                st.table(license_df)
                
                if total_additional_licenses > 0:
                    increase_pct = (total_additional_licenses / total_current_licenses * 100) if total_current_licenses > 0 else 0
                    st.info(f"You're adding {int(total_additional_licenses)} licenses ({increase_pct:.1f}% increase).")
                
                with st.expander("Current vs. New Cost Summary", expanded=True):
                    # Create a comparison table with billing term-specific labels
                    if billing_term == 'Monthly':
                        current_cost_monthly = total_current_cost / 12
                        new_cost_monthly = total_updated_annual_cost / 12
                        
                        comparison_data = {
                            "Cost Type": ["Current Monthly Cost", "New Monthly Cost", "Difference", "Percentage Change"],
                            "Amount": [
                                f"${current_cost_monthly:,.2f}",
                                f"${new_cost_monthly:,.2f}",
                                f"${new_cost_monthly - current_cost_monthly:,.2f}",
                                f"{((new_cost_monthly - current_cost_monthly) / current_cost_monthly * 100) if current_cost_monthly > 0 else 0:,.2f}%"
                            ]
                        }
                        
                        comparison_df = pd.DataFrame(comparison_data)
                        st.table(comparison_df)
                        
                        # Add insight about the cost change
                        if new_cost_monthly > current_cost_monthly:
                            change_pct = ((new_cost_monthly - current_cost_monthly) / current_cost_monthly * 100) if current_cost_monthly > 0 else 0
                            st.info(f"The new monthly cost represents a {change_pct:.1f}% increase from the current cost.")
                        elif new_cost_monthly < current_cost_monthly:
                            change_pct = ((current_cost_monthly - new_cost_monthly) / current_cost_monthly * 100) if current_cost_monthly > 0 else 0
                            st.success(f"The new monthly cost represents a {change_pct:.1f}% decrease from the current cost.")
                        else:
                            st.info("The new monthly cost is identical to the current cost.")
                    else:
                        # For Annual and Prepaid, show annual costs
                        comparison_data = {
                            "Cost Type": ["Current Annual Cost", "New Annual Cost", "Difference", "Percentage Change"],
                            "Amount": [
                                f"${total_current_cost:,.2f}",
                                f"${total_updated_annual_cost:,.2f}",
                                f"${total_updated_annual_cost - total_current_cost:,.2f}",
                                f"{((total_updated_annual_cost - total_current_cost) / total_current_cost * 100) if total_current_cost > 0 else 0:,.2f}%"
                            ]
                        }
                        
                        comparison_df = pd.DataFrame(comparison_data)
                        st.table(comparison_df)
                        
                        # Add insight about the cost change
                        if total_updated_annual_cost > total_current_cost:
                            change_pct = ((total_updated_annual_cost - total_current_cost) / total_current_cost * 100) if total_current_cost > 0 else 0
                            st.info(f"The new annual cost represents a {change_pct:.1f}% increase from the current cost.")
                        elif total_updated_annual_cost < total_current_cost:
                            change_pct = ((total_current_cost - total_updated_annual_cost) / total_current_cost * 100) if total_current_cost > 0 else 0
                            st.success(f"The new annual cost represents a {change_pct:.1f}% decrease from the current cost.")
                        else:
                            st.info("The new annual cost is identical to the current cost.")
                
                st.markdown("### Cost Comparison")
                
                # Prepare chart data based on billing term
                if billing_term == 'Monthly':
                    # Get values from the Total Services Cost row
                    total_row = processed_data[processed_data['Cloud Service Description'] == 'Total Services Cost']
                    monthly_co_termed = float(total_row['Monthly Co-Termed Cost'].iloc[0]) if 'Monthly Co-Termed Cost' in total_row.columns else 0.0
                    first_month_co_termed = float(total_row['First Month Co-Termed Cost'].iloc[0]) if 'First Month Co-Termed Cost' in total_row.columns else 0.0
                    
                    # Current monthly cost
                    current_monthly = total_current_cost / 12
                    
                    chart_data = {
                        "currentCost": float(current_monthly),
                        "coTermedMonthly": first_month_co_termed,
                        "newMonthly": monthly_co_termed,
                        "subscription": float(total_subscription_term_fee)
                    }
                elif billing_term == 'Annual':
                    chart_data = {
                        "currentCost": float(total_current_cost),
                        "firstYearCoTerm": float(total_first_year_cost),
                        "newAnnual": float(total_updated_annual_cost),
                        "subscription": float(total_subscription_term_fee)
                    }
                elif billing_term == 'Prepaid':
                    chart_data = {
                        "currentCost": float(total_current_cost),
                        "coTermedPrepaid": float(total_prepaid_cost),
                        "subscription": float(total_subscription_term_fee)
                    }
                
                # Now generate the chart using the updated chart data
                try:
                    # Convert all values to float and ensure they're not None
                    for key in chart_data:
                        if chart_data[key] is None:
                            chart_data[key] = 0.0
                        else:
                            chart_data[key] = float(chart_data[key])
                    
                    # Render chart with safety measures
                    components.html(
                        CHART_HTML + f"""
                        <script>
                            console.log("Starting chart rendering...");
                            try {{
                                const chartData = {chart_data};
                                console.log("Chart data:", JSON.stringify(chartData));
                                renderChart(chartData, '{billing_term}', '{st.session_state.theme}');
                                console.log("Chart rendering complete");
                            }} catch (e) {{
                                console.error("Error rendering chart:", e);
                                document.write("<div style='color:red'>Error rendering chart: " + e.message + "</div>");
                            }}
                        </script>
                        """,
                        height=500
                    )
                except Exception as e:
                    st.error(f"Error generating chart: {str(e)}")
                    st.warning("Please try recalculating costs or refreshing the page.")
                
                # Generate PDF
                st.subheader("Report Generation")
                
                # Create columns for download options
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("##### PDF Report")
                    pdf_buffer = generate_pdf(
                        billing_term,
                        months_remaining,
                        extension_months,
                        total_current_cost,
                        total_prepaid_cost,
                        total_first_year_cost,
                        total_updated_annual_cost,
                        total_subscription_term_fee,
                        processed_data,
                        agreement_term,
                        customer_name,
                        customer_email,
                        account_manager,
                        company_name,
                        logo_path
                    )
                    
                    st.download_button(
                        label="Download PDF Report",
                        data=pdf_buffer,
                        file_name=f"{customer_name.replace(' ', '_')}_coterming_report.pdf" if customer_name else "coterming_report.pdf",
                        mime="application/pdf",
                        key="pdf_download"
                    )
        
        # No navigation buttons
            
    with tabs[4]:
        st.markdown('<div class="sub-header">Email Template</div>', unsafe_allow_html=True)
        
        # Check if we have calculation results
        if st.session_state.calculation_results:
            results = st.session_state.calculation_results
            total_current_cost = results["total_current_cost"]
            total_prepaid_cost = results["total_prepaid_cost"]
            total_first_year_cost = results["total_first_year_cost"]
            total_updated_annual_cost = results["total_updated_annual_cost"] 
            total_subscription_term_fee = results["total_subscription_term_fee"]
            
            # Determine which cost value to use based on billing term
            if billing_term == 'Monthly':
                first_cost = results["processed_data"][results["processed_data"]['Cloud Service Description'] == 'Total Services Cost']['First Month Co-Termed Cost'].iloc[0]
            elif billing_term == 'Annual':
                first_cost = total_first_year_cost
            else:  # Prepaid
                first_cost = total_prepaid_cost
            
            # Generate email template
            email_content = generate_email_template(
                billing_term,
                customer_name if customer_name else "[Customer Name]",
                total_current_cost,
                first_cost,
                total_subscription_term_fee,
                company_name if company_name else "[Your Company]",
                account_manager if account_manager else "[Account Manager]",
                total_updated_annual_cost
            )
            
            # Display email template with copy button
            st.markdown("### Email Template Preview")
            st.markdown('<div class="email-template">' + email_content.replace('\n', '<br>') + '</div>', unsafe_allow_html=True)
            
            # Add copy to clipboard button
            st.markdown(copy_to_clipboard_button(email_content, "Copy Email Template"), unsafe_allow_html=True)
            
            # Email subject suggestion
            st.markdown("### Suggested Email Subject")
            email_subject = f"Co-Terming Cost Proposal - {customer_name if customer_name else '[Customer Name]'}"
            st.text_input("Subject Line:", value=email_subject, key="email_subject")
            
            # Add copy button for subject line
            st.markdown(copy_to_clipboard_button(email_subject, "Copy Subject Line"), unsafe_allow_html=True)
        else:
            st.info("Please calculate costs first to generate an email template.")
        
        # No navigation buttons

elif st.session_state.active_tab == 'help_documentation':
    st.markdown('<div class="main-header">Help & Documentation</div>', unsafe_allow_html=True)
    
    # Create an accordion for different help topics
    with st.expander("How to Use This Calculator", expanded=True):
        st.markdown("""
        ### Basic Usage
        
        1. **Agreement Information**: Enter the basic details of the agreement, including billing term, agreement duration, and months remaining.
        
        2. **Customer Information**: Enter the customer details to personalize the report and email template.
        
        3. **Service Information**: Add the services that are part of the agreement, including quantities and fees.
        
        4. **Calculate Costs**: Click the 'Calculate Costs' button to generate the results.
        
        5. **Generate Reports**: After calculation, you can download a PDF report or use the generated email template.
        
        6. **Navigation**: Use the 'Next' and 'Back' buttons at the bottom of each page to move between tabs.
        """)
    
    with st.expander("Understanding Billing Terms"):
        st.markdown("""
        ### Billing Terms Explained
        
        - **Annual**: Billing occurs once per year. The calculator shows the first year co-termed cost and the updated annual cost.
        
        - **Monthly**: Billing occurs monthly. The calculator shows the first month co-termed cost and the monthly recurring cost.
        
        - **Prepaid**: The entire subscription period is paid upfront. The calculator shows the total prepaid cost.
        """)
    
    with st.expander("Calculation Methodology"):
        st.markdown("""
        ### How Costs Are Calculated
        
        - **First Month Co-Termed Cost**: For monthly billing, this represents the prorated cost for the first month based on the remaining fraction of the month.
        
        - **First Year Co-Termed Cost**: For annual billing, this represents the prorated cost for the first year based on the remaining months in the year.
        
        - **Updated Annual Cost**: This is the new annual cost after adding the additional licenses.
        
        - **Subscription Term Total Service Fee**: This is the total cost over the entire subscription period, including the extension if applicable.
        """)
    
    with st.expander("Customizing Reports and Emails"):
        st.markdown("""
        ### Customization Options
        
        - **Company Logo**: Upload your company logo in the sidebar to include it in the PDF report.
        
        - **Theme**: Switch between light and dark themes in the sidebar.
        
        - **Email Template**: The email template is automatically generated based on the calculation results and customer information. You can copy and customize it as needed.
        """)

elif st.session_state.active_tab == 'about':
    st.markdown('<div class="main-header">About This Application</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### Co-Terming Cost Calculator
    
    This application helps sales teams calculate and communicate the costs of co-terming subscription services. It supports various billing terms and provides detailed reports and email templates.
    
    ### Features
    
    - Support for Annual, Monthly, and Prepaid billing terms
    - Customizable service line items
    - Detailed cost breakdown and visualizations
    - PDF report generation
    - Email template generation
    - Light and dark themes
    - Company logo customization
    - Easy tab navigation with Next/Back buttons
    
    ### Version History
    
    - **v1.2** (Current): Added Next/Back navigation buttons for improved user experience
    - **v1.1**: Added customer information, email templates, and theme options
    - **v1.0**: Initial release with basic calculation features
    
    ### Contact
    
    For support or feature requests, please contact your application administrator.
    """)
    
    # Footer with a credit note
    st.markdown("""
    <div class="footer">
    &copy; 2024 Your Company. All rights reserved.
    </div>
    """, unsafe_allow_html=True)

# Add a footer to the main application
st.markdown("""
<div class="footer">
Co-Terming Cost Calculator v1.2 | Developed by Your Team
</div>
""", unsafe_allow_html=True)
 + value.toLocaleString(undefined, {
                                    minimumFractionDigits: 2,
                                    maximumFractionDigits: 2
                                });
                            },
                            font: {
                                weight: 'bold',
                                size: 12
                            },
                            color: colors.textColor,
                            offset: 8
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    let value = context.raw;
                                    return `${context.dataset.label}: ${value.toLocaleString(undefined, {
                                        minimumFractionDigits: 2,
                                        maximumFractionDigits: 2
                                    })}`;
                                }
                            }
                        }
                    },
                    layout: {
                        padding: {
                            top: 10,
                            bottom: 10
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: colors.gridColor
                            },
                            ticks: {
                                color: colors.textColor,
                                callback: function(value) {
                                    return '

def calculate_costs(df, agreement_term, months_remaining, extension_months, billing_term):
    total_term = months_remaining + extension_months
    months_elapsed = agreement_term - months_remaining
    total_prepaid_cost = 0
    total_first_year_cost = 0
    total_updated_annual_cost = 0
    total_subscription_term_fee = 0
    total_current_cost = 0  # Current cost before additional licenses

    for index, row in df.iterrows():
        # Calculate current costs (before additional licenses)
        current_monthly_cost = (row['Annual Unit Fee'] / 12) * row['Unit Quantity']
        current_annual_cost = row['Unit Quantity'] * row['Annual Unit Fee']
        
        # Calculate costs with additional licenses
        first_month_co_termed_cost = (row['Annual Unit Fee'] / 12) * row['Additional Licenses'] * (months_remaining % 1) if billing_term == 'Monthly' else 0
        monthly_co_termed_cost = (row['Annual Unit Fee'] / 12) * row['Additional Licenses'] if billing_term == 'Monthly' else 0
        annual_total_fee = row['Unit Quantity'] * row['Annual Unit Fee']
        subscription_term_total_fee = ((annual_total_fee * total_term) / 12) + ((row['Additional Licenses'] * row['Annual Unit Fee'] * total_term) / 12)
        co_termed_prepaid_cost = (row['Additional Licenses'] * row['Annual Unit Fee'] * total_term) / 12 if billing_term == 'Prepaid' else 0
        co_termed_first_year_cost = (row['Additional Licenses'] * row['Annual Unit Fee'] * (12 - (months_elapsed % 12))) / 12 if billing_term == 'Annual' else 0
        updated_annual_cost = annual_total_fee + (row['Additional Licenses'] * row['Annual Unit Fee']) if billing_term == 'Annual' else 0

        # Store calculated values in the dataframe based on billing term
        if billing_term == 'Monthly':
            df.at[index, 'Current Monthly Cost'] = current_monthly_cost
            df.at[index, 'First Month Co-Termed Cost'] = first_month_co_termed_cost
            df.at[index, 'Monthly Co-Termed Cost'] = monthly_co_termed_cost
        elif billing_term == 'Annual':
            df.at[index, 'Current Annual Cost'] = current_annual_cost
            df.at[index, 'First Year Co-Termed Cost'] = co_termed_first_year_cost
            df.at[index, 'Updated Annual Cost'] = updated_annual_cost
        else:  # Prepaid
            df.at[index, 'Current Annual Cost'] = current_annual_cost
            df.at[index, 'Prepaid Co-Termed Cost'] = co_termed_prepaid_cost
            
        # Always add the subscription term total
        df.at[index, 'Subscription Term Total Service Fee'] = subscription_term_total_fee

    # Convert numeric columns to float - only convert columns that exist
    numeric_cols = [
        "Annual Unit Fee", "Current Monthly Cost", "Current Annual Cost", "Prepaid Co-Termed Cost",
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
    if 'Current Annual Cost' in df.columns:
        total_current_cost = df.loc[df['Cloud Service Description'] != 'Total Services Cost', 'Current Annual Cost'].sum()
    if 'Prepaid Co-Termed Cost' in df.columns:
        total_prepaid_cost = df.loc[df['Cloud Service Description'] != 'Total Services Cost', 'Prepaid Co-Termed Cost'].sum()
    if 'First Year Co-Termed Cost' in df.columns:
        total_first_year_cost = df.loc[df['Cloud Service Description'] != 'Total Services Cost', 'First Year Co-Termed Cost'].sum()
    if 'Updated Annual Cost' in df.columns:
        total_updated_annual_cost = df.loc[df['Cloud Service Description'] != 'Total Services Cost', 'Updated Annual Cost'].sum()
    if 'Subscription Term Total Service Fee' in df.columns:
        total_subscription_term_fee = df.loc[df['Cloud Service Description'] != 'Total Services Cost', 'Subscription Term Total Service Fee'].sum()

    return df, total_current_cost, total_prepaid_cost, total_first_year_cost, total_updated_annual_cost, total_subscription_term_fee

def generate_pdf(billing_term, months_remaining, extension_months, total_current_cost, total_prepaid_cost, 
                total_first_year_cost, total_updated_annual_cost, total_subscription_term_fee, data, agreement_term, 
                customer_name="", customer_email="", account_manager="", company_name="", logo_path=None):
    pdf = FPDF(orientation='L')
    pdf.add_page()
    pdf.set_font("Arial", "B", 10)
    
    # Add logo if provided
    if logo_path and os.path.exists(logo_path):
        try:
            pdf.image(logo_path, x=10, y=10, w=50)
        except Exception as e:
            print(f"Could not add logo: {e}")
    
    # Add title
    pdf.cell(280, 8, "Co-Terming Cost Report", ln=True, align="C")
    pdf.ln(4)
    
    # Move content down to make room for logo if needed
    pdf.set_y(50)
    
    # Adjust column widths for landscape
    w_desc = 75
    w_qty = 30
    w_fee = 30
    w_lic = 30
    w_cost = 40
    w_total = 60

    # Customer Information Section
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Customer Information", ln=True, align="L")
    pdf.set_font("Arial", "", 10)
    
    pdf.cell(100, 6, f"Customer: {customer_name}", ln=False)
    pdf.cell(0, 6, f"Contact Email: {customer_email}", ln=True)
    
    pdf.cell(100, 6, f"Account Manager: {account_manager}", ln=False)
    pdf.cell(0, 6, f"Company: {company_name}", ln=True)
    
    pdf.ln(5)
    
    # Agreement Information Section
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Agreement Information", ln=True, align="L")
    pdf.set_font("Arial", "", 10)
    
    # Left side of header
    pdf.cell(100, 6, f"Date: {datetime.today().strftime('%Y-%m-%d')}", ln=False)
    pdf.cell(0, 6, f"Agreement Term: {agreement_term:.2f} months", ln=True)
    
    pdf.cell(0, 6, f"Extension Period: {extension_months} months", ln=True)
    
    pdf.cell(100, 6, f"Billing Term: {billing_term}", ln=False)
    pdf.cell(0, 6, f"Total Term: {months_remaining + extension_months:.2f} months", ln=True)
    
    pdf.ln(10)
    
    # Cost Summary Section
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Cost Summary", ln=True, align="L")
    pdf.set_font("Arial", "", 10)
    
    # Add current cost information
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 6, f"Current Annual Cost (Before Additional Licenses): ${total_current_cost:,.2f}", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.ln(5)
    
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
        pdf.cell(100, 6, "", ln=False)  # Empty left column
        pdf.cell(0, 6, f"Updated Annual Cost: ${total_updated_annual_cost:,.2f}", ln=True)
    
    pdf.ln(10)
    
    # Detailed Line Items
    pdf.set_font("Arial", "B", 7)
    pdf.cell(200, 5, "Detailed Line Items", ln=True)
    
    # Print headers
    pdf.set_font("Arial", "B", 7)
    
    # Print headers in a single row using cell method
    pdf.cell(w_desc, 6, 'Cloud Service Description', 1, 0, 'C')
    pdf.cell(w_qty, 6, 'Unit Quantity', 1, 0, 'C')
    pdf.cell(w_fee, 6, 'Annual Unit Fee', 1, 0, 'C')
    pdf.cell(w_lic, 6, 'Additional Licenses', 1, 0, 'C')
    pdf.cell(w_cost, 6, columns[-2]['title'], 1, 0, 'C')
    pdf.cell(w_total, 6, columns[-1]['title'], 1, 1, 'C')
    
    # Add a small line break
    pdf.ln(1)

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
    
    # Add footer with company information
    pdf.ln(10)
    pdf.set_font("Arial", "I", 8)
    pdf.cell(0, 6, f"Generated by {company_name}", 0, 0, 'C')

    pdf_buffer = io.BytesIO()
    pdf.output(pdf_buffer)
    pdf_buffer.seek(0)
    
    return pdf_buffer

def generate_email_template(billing_term, customer_name, current_cost, first_cost, total_subscription_cost, company_name, account_manager, updated_annual_cost=0):
    # Format currency values first
    current_cost_fmt = "${:,.2f}".format(current_cost)
    first_cost_fmt = "${:,.2f}".format(first_cost)
    total_cost_fmt = "${:,.2f}".format(total_subscription_cost)
    updated_cost_fmt = "${:,.2f}".format(updated_annual_cost)
    
    # Start building template
    template = "Dear " + str(customer_name) + ",\n\n"
    
    if billing_term == "Monthly":
        template += "We are writing to inform you about the updated co-terming cost for your monthly billing arrangement.\n\n"
        template += "Current Agreement:\n"
        template += "- Current Annual Cost: " + current_cost_fmt + "\n\n"
        template += "Updated Cost Summary:\n"
        template += "- First Month Co-Termed Cost: " + first_cost_fmt + "\n"
        template += "- Total Subscription Cost: " + total_cost_fmt + "\n"
        
        if updated_annual_cost > 0:
            template += "- Updated Annual Cost: " + updated_cost_fmt + "\n"
        
        template += "\nKey Details:\n"
        template += "- The first month's co-termed cost reflects your current service adjustments.\n"
        template += "- Your total subscription cost covers the entire term of the agreement.\n"
    
    elif billing_term == "Annual":
        template += "We are writing to inform you about the updated co-terming cost for your annual billing arrangement.\n\n"
        template += "Current Agreement:\n"
        template += "- Current Annual Cost: " + current_cost_fmt + "\n\n"
        template += "Updated Cost Summary:\n"
        template += "- First Year Co-Termed Cost: " + first_cost_fmt + "\n"
        template += "- Updated Annual Cost: " + updated_cost_fmt + "\n"
        template += "- Total Subscription Cost: " + total_cost_fmt + "\n"
        
        template += "\nKey Details:\n"
        template += "- The first year's co-termed cost reflects your current service adjustments.\n"
        template += "- Your total subscription cost covers the entire term of the agreement.\n"
    
    elif billing_term == "Prepaid":
        template += "We are writing to inform you about the updated co-terming cost for your prepaid billing arrangement.\n\n"
        template += "Current Agreement:\n"
        template += "- Current Annual Cost: " + current_cost_fmt + "\n\n"
        template += "Updated Cost Summary:\n"
        template += "- Total Pre-Paid Cost: " + first_cost_fmt + "\n"
        template += "- Total Subscription Cost: " + total_cost_fmt + "\n"
        
        if updated_annual_cost > 0:
            template += "- Updated Annual Cost: " + updated_cost_fmt + "\n"
        
        template += "\nKey Details:\n"
        template += "- The pre-paid cost covers your entire service term.\n"
        template += "- Your total subscription cost reflects the full agreement period.\n"
    
    else:
        return "Invalid billing term"
    
    # Add common footer sections
    template += "\nNext Steps:\n"
    template += "1. Please carefully review the cost breakdown above.\n"
    template += "2. If you approve these terms, kindly reply to this email with your confirmation.\n"
    template += "3. If you have any questions or concerns, please contact our sales team.\n\n"
    template += "We appreciate your continued business and look forward to your approval.\n\n"
    template += "Best regards,\n"
    template += str(account_manager) + "\n"
    template += str(company_name) + " Sales Team"
    
    return template
    
    # Return the appropriate template based on billing term
    return email_templates.get(billing_term, "Invalid billing term")

def copy_to_clipboard_button(text, button_text="Copy to Clipboard"):
    # Create a unique key for this button
    import hashlib
    button_id = "copy_button_" + hashlib.md5(text.encode()).hexdigest()[:8]
    
    # Create the JavaScript function
    js_code = """
<script>
function copyToClipboard_%s() {
    const el = document.createElement('textarea');
    el.value = `%s`;
    document.body.appendChild(el);
    el.select();
    document.execCommand('copy');
    document.body.removeChild(el);
    
    // Change button text temporarily
    const btn = document.getElementById('%s');
    const originalText = btn.innerHTML;
    btn.innerHTML = 'Copied!';
    setTimeout(() => {
        btn.innerHTML = originalText;
    }, 2000);
}
</script>
""" % (button_id, text.replace('`', '\\`'), button_id)
    
    # Create the HTML button (all on one line to avoid syntax issues)
    button_html = "<button id='%s' onclick='copyToClipboard_%s()' style='background-color: #4CAF50; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; margin-top: 10px;'>%s</button>" % (button_id, button_id, button_text)
    
    # Combine the JavaScript and HTML
    return js_code + button_html

# Navigation function remains for potential future use
# No navigation buttons

# Sidebar for navigation and settings
with st.sidebar:
    st.image("https://via.placeholder.com/150x50.png?text=Your+Logo", width=150)
    st.title("Navigation")
    
    # Navigation menu
    nav_options = ["Calculator", "Help & Documentation", "About"]
    nav_selection = st.radio("Go to:", nav_options)
    
    # Set the active tab based on navigation selection
    st.session_state.active_tab = nav_selection.lower().replace(" & ", "_").replace(" ", "_")
    
    st.markdown("---")
    
    # Theme toggle
    st.subheader("Settings")
    theme_options = ["Light", "Dark"]
    selected_theme = st.radio("Theme:", theme_options, index=0 if st.session_state.theme == 'light' else 1)
    st.session_state.theme = selected_theme.lower()
    
    st.markdown("---")
    
    # Uploader for logo
    st.subheader("Company Logo")
    uploaded_logo = st.file_uploader("Upload your logo for PDF reports", type=["png", "jpg", "jpeg"])
    if uploaded_logo:
        # Save the uploaded file
        logo_path = "logo.png"
        with open(logo_path, "wb") as f:
            f.write(uploaded_logo.getbuffer())
        st.success("Logo uploaded successfully!")
    else:
        logo_path = None
    
    st.markdown("---")
    
    # App info
    st.markdown("##### Co-Terming Calculator v1.1")
    st.markdown("© 2024 Your Company")

# Main content area
if st.session_state.active_tab in ['calculator', 'results']:
    # Custom HTML header
    st.markdown('<div class="main-header">Co-Terming Cost Calculator</div>', unsafe_allow_html=True)
    
    # Create tabs for different sections of the calculator
    tab_titles = ["Agreement Info", "Customer Info", "Services", "Results", "Email Template"]
    
    # Set the active tab based on session state
    active_tab_index = st.session_state.current_tab
    tabs = st.tabs(tab_titles)
    
    with tabs[0]:
        st.markdown('<div class="sub-header">Agreement Information</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            current_date = datetime.today().strftime('%Y-%m-%d')
            st.text(f"Current Date: {current_date}")
            billing_term = st.selectbox("Billing Term:", ["Annual", "Prepaid", "Monthly"])
            # Add date picker for agreement start date
            agreement_start_date = st.date_input("Agreement Start Date:", 
                                               value=date.today() - relativedelta(months=6),
                                               max_value=date.today())
        
        with col2:
            agreement_term = st.number_input("Agreement Term (Months):", min_value=1, value=36, step=1, format="%d")
            
            # Calculate months remaining based on start date and agreement term with day precision
            today = date.today()
            
            # Calculate full months passed
            months_passed = relativedelta(today, agreement_start_date).years * 12 + relativedelta(today, agreement_start_date).months
            
            # Calculate the day fraction of the current month
            # Get days in the current month
            if today.month == 12:
                last_day_of_month = date(today.year + 1, 1, 1) - relativedelta(days=1)
            else:
                last_day_of_month = date(today.year, today.month + 1, 1) - relativedelta(days=1)
            
            days_in_month = last_day_of_month.day
            day_fraction = (days_in_month - today.day) / days_in_month
            
            # Add the day fraction to get precise months passed
            precise_months_passed = months_passed + (1 - day_fraction)
            
            # Calculate remaining months with precision
            calculated_months_remaining = max(0, agreement_term - precise_months_passed)
            
            # Display calculated months remaining with 2 decimal precision
            st.text(f"Calculated Months Remaining: {calculated_months_remaining:.2f}")
            
            # Allow manual override of months remaining
            months_remaining = st.number_input("Override Months Remaining (if needed):", 
                                             min_value=0.0, 
                                             max_value=float(agreement_term), 
                                             value=float(calculated_months_remaining), 
                                             step=0.01, 
                                             format="%.2f")
        
        # Add extension period option
        add_extension = st.checkbox("Add Agreement Extension?")
        if add_extension:
            extension_months = st.number_input("Extension Period (Months):", min_value=1, value=12, step=1, format="%d")
            total_term = months_remaining + extension_months
            st.info(f"Total Term: {total_term:.2f} months")
        else:
            extension_months = 0
            total_term = months_remaining
        
        # No navigation buttons
            
    with tabs[1]:
        st.markdown('<div class="sub-header">Customer Information</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            customer_name = st.text_input("Customer Name:", placeholder="Enter customer name")
            customer_email = st.text_input("Customer Email:", placeholder="Enter customer email")
        
        with col2:
            account_manager = st.text_input("Account Manager:", placeholder="Enter account manager name")
            company_name = st.text_input("Your Company:", value="Your Company Name", placeholder="Enter your company name")
        
        # No navigation buttons
            
    with tabs[2]:
        st.markdown('<div class="sub-header">Service Information</div>', unsafe_allow_html=True)
        
        num_items = st.number_input("Number of Line Items:", min_value=1, value=1, step=1, format="%d")
        
        columns = ["Cloud Service Description", "Unit Quantity", "Annual Unit Fee", "Additional Licenses", 
                  "Prepaid Co-Termed Cost", "First Year Co-Termed Cost", "Updated Annual Cost", 
                  "Subscription Term Total Service Fee", "Monthly Co-Termed Cost", "First Month Co-Termed Cost"]
        data = pd.DataFrame(columns=columns)
        
        # Define numeric columns for proper handling
        numeric_cols = [
            "Annual Unit Fee", "Current Monthly Cost", "Current Annual Cost", "Prepaid Co-Termed Cost",
            "First Year Co-Termed Cost", "Updated Annual Cost", "Subscription Term Total Service Fee",
            "Monthly Co-Termed Cost", "First Month Co-Termed Cost"
        ]
        
        # Create a container for the line items
        line_items_container = st.container()
        
        with line_items_container:
            for i in range(num_items):
                st.markdown(f"**Item {i+1}**")
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                
                # Use a unique key for each input to avoid conflicts
                service_key = f"service_{i}"
                qty_key = f"qty_{i}"
                fee_key = f"fee_{i}"
                add_lic_key = f"add_lic_{i}"
                
                        # Create input fields for each row
                service = col1.text_input("Service Description", key=service_key, placeholder="Enter service name")
                qty = col2.number_input("Quantity", min_value=0, value=1, step=1, format="%d", key=qty_key)
                fee = col3.number_input("Annual Fee ($)", min_value=0.0, value=1000.0, step=100.0, format="%.2f", key=fee_key)
                add_lic = col4.number_input("Add. Licenses", min_value=0, value=0, step=1, format="%d", key=add_lic_key)
                
                # Add the row data to our dataframe
                row_data = {
                    "Cloud Service Description": service if service else "",
                    "Unit Quantity": qty,
                    "Annual Unit Fee": fee,
                    "Additional Licenses": add_lic,
                }
                
                # Fill in missing columns with empty values or zeros
                for col in columns:
                    if col not in row_data:
                        row_data[col] = 0 if col in numeric_cols else ""
                        
                # Append to the dataframe
                new_row = pd.DataFrame([row_data])
                data = pd.concat([data, new_row], ignore_index=True)
        
        # Add validation for empty service descriptions
        empty_services = data["Cloud Service Description"].isnull() | (data["Cloud Service Description"] == "")
        if empty_services.any():
            st.warning("⚠️ Please enter a description for all services.")
        
        # Store service data in session state
        st.session_state.service_data = data
        
        # No navigation buttons
            
    with tabs[3]:
        st.markdown('<div class="sub-header">Results</div>', unsafe_allow_html=True)
        
        # Check if we have service data in session state from the Services tab
        if 'service_data' in st.session_state:
            data = st.session_state.service_data
            valid_data = True
        else:
            # Check if we have valid data before calculating
            valid_data = not empty_services.any() and len(data) > 0
        
        # Create a placeholder for calculation results
        results_placeholder = st.empty()
        
        # Calculate button on the results page
        calculate_button = st.button("Calculate Costs", disabled=not valid_data, 
                                     help="Enter all required information to enable calculations")
        
        # Store calculation results in session state
        if "calculation_results" not in st.session_state:
            st.session_state.calculation_results = None
            
        if calculate_button and valid_data:
            with st.spinner("Calculating costs..."):
                # Calculate costs
                processed_data, total_current_cost, total_prepaid_cost, total_first_year_cost, total_updated_annual_cost, total_subscription_term_fee = calculate_costs(
                    data,
                    agreement_term,
                    months_remaining,
                    extension_months,
                    billing_term
                )
                
                # Store results in session state
                st.session_state.calculation_results = {
                    "processed_data": processed_data,
                    "total_current_cost": total_current_cost,
                    "total_prepaid_cost": total_prepaid_cost,
                    "total_first_year_cost": total_first_year_cost,
                    "total_updated_annual_cost": total_updated_annual_cost,
                    "total_subscription_term_fee": total_subscription_term_fee
                }
                
            st.success("Calculations completed successfully!")
            
        # Display results if available
        if st.session_state.calculation_results:
            results = st.session_state.calculation_results
            processed_data = results["processed_data"]
            total_current_cost = results["total_current_cost"]
            total_prepaid_cost = results["total_prepaid_cost"]
            total_first_year_cost = results["total_first_year_cost"]
            total_updated_annual_cost = results["total_updated_annual_cost"]
            total_subscription_term_fee = results["total_subscription_term_fee"]
            
            with results_placeholder.container():
                st.subheader("Detailed Line Items")
                
                # Handle column dropping more thoroughly
                columns_to_drop = []
                if billing_term == 'Monthly':
                    columns_to_drop = ['Prepaid Co-Termed Cost', 'First Year Co-Termed Cost', 'Updated Annual Cost', 'Current Annual Cost']
                elif billing_term == 'Annual':
                    columns_to_drop = ['Prepaid Co-Termed Cost', 'Monthly Co-Termed Cost', 'First Month Co-Termed Cost', 'Current Monthly Cost']
                elif billing_term == 'Prepaid':
                    columns_to_drop = ['Monthly Co-Termed Cost', 'First Month Co-Termed Cost', 'First Year Co-Termed Cost', 'Updated Annual Cost', 'Current Monthly Cost']
                
                # Only drop columns that exist in the dataframe
                displayed_data = processed_data.copy()
                existing_columns_to_drop = [col for col in columns_to_drop if col in displayed_data.columns]
                if existing_columns_to_drop:
                    displayed_data = displayed_data.drop(columns=existing_columns_to_drop)
                
                # Format numeric columns
                for col in ["Annual Unit Fee", "Prepaid Co-Termed Cost", "First Year Co-Termed Cost", 
                            "Updated Annual Cost", "Subscription Term Total Service Fee", 
                            "Monthly Co-Termed Cost", "First Month Co-Termed Cost"]:
                    if col in displayed_data.columns:
                        displayed_data[col] = pd.to_numeric(displayed_data[col], errors='coerce')
                
                # Display the dataframe with formatting
                st.dataframe(displayed_data.style.format({
                    "Annual Unit Fee": "${:,.2f}",
                    "Prepaid Co-Termed Cost": "${:,.2f}",
                    "First Year Co-Termed Cost": "${:,.2f}",
                    "Updated Annual Cost": "${:,.2f}",
                    "Subscription Term Total Service Fee": "${:,.2f}",
                    "Monthly Co-Termed Cost": "${:,.2f}",
                    "First Month Co-Termed Cost": "${:,.2f}"
                }).set_properties(**{"white-space": "normal"}))
                
                # Show current cost summary based on billing term
                st.markdown("### Current Agreement Cost")
                
                if billing_term == 'Monthly':
                    # Show only monthly cost for Monthly billing term
                    current_monthly = total_current_cost / 12
                    st.markdown(f"**Current Monthly Cost:** ${current_monthly:,.2f}")
                else:
                    # Show only annual cost for Annual and Prepaid billing terms
                    st.markdown(f"**Current Annual Cost:** ${total_current_cost:,.2f}")
                
                # Calculate total licenses (current + additional)
                total_current_licenses = processed_data[processed_data['Cloud Service Description'] != 'Total Services Cost']['Unit Quantity'].sum()
                total_additional_licenses = processed_data[processed_data['Cloud Service Description'] != 'Total Services Cost']['Additional Licenses'].sum()
                total_licenses = total_current_licenses + total_additional_licenses
                
                # Display license summary
                st.markdown("### License Summary")
                license_data = {
                    "License Type": ["Current Licenses", "Additional Licenses", "Total Licenses"],
                    "Count": [
                        f"{int(total_current_licenses)}",
                        f"{int(total_additional_licenses)}",
                        f"{int(total_licenses)}"
                    ]
                }
                
                license_df = pd.DataFrame(license_data)
                st.table(license_df)
                
                if total_additional_licenses > 0:
                    increase_pct = (total_additional_licenses / total_current_licenses * 100) if total_current_licenses > 0 else 0
                    st.info(f"You're adding {int(total_additional_licenses)} licenses ({increase_pct:.1f}% increase).")
                
                with st.expander("Current vs. New Cost Summary", expanded=True):
                    # Create a comparison table with billing term-specific labels
                    if billing_term == 'Monthly':
                        current_cost_monthly = total_current_cost / 12
                        new_cost_monthly = total_updated_annual_cost / 12
                        
                        comparison_data = {
                            "Cost Type": ["Current Monthly Cost", "New Monthly Cost", "Difference", "Percentage Change"],
                            "Amount": [
                                f"${current_cost_monthly:,.2f}",
                                f"${new_cost_monthly:,.2f}",
                                f"${new_cost_monthly - current_cost_monthly:,.2f}",
                                f"{((new_cost_monthly - current_cost_monthly) / current_cost_monthly * 100) if current_cost_monthly > 0 else 0:,.2f}%"
                            ]
                        }
                        
                        comparison_df = pd.DataFrame(comparison_data)
                        st.table(comparison_df)
                        
                        # Add insight about the cost change
                        if new_cost_monthly > current_cost_monthly:
                            change_pct = ((new_cost_monthly - current_cost_monthly) / current_cost_monthly * 100) if current_cost_monthly > 0 else 0
                            st.info(f"The new monthly cost represents a {change_pct:.1f}% increase from the current cost.")
                        elif new_cost_monthly < current_cost_monthly:
                            change_pct = ((current_cost_monthly - new_cost_monthly) / current_cost_monthly * 100) if current_cost_monthly > 0 else 0
                            st.success(f"The new monthly cost represents a {change_pct:.1f}% decrease from the current cost.")
                        else:
                            st.info("The new monthly cost is identical to the current cost.")
                    else:
                        # For Annual and Prepaid, show annual costs
                        comparison_data = {
                            "Cost Type": ["Current Annual Cost", "New Annual Cost", "Difference", "Percentage Change"],
                            "Amount": [
                                f"${total_current_cost:,.2f}",
                                f"${total_updated_annual_cost:,.2f}",
                                f"${total_updated_annual_cost - total_current_cost:,.2f}",
                                f"{((total_updated_annual_cost - total_current_cost) / total_current_cost * 100) if total_current_cost > 0 else 0:,.2f}%"
                            ]
                        }
                        
                        comparison_df = pd.DataFrame(comparison_data)
                        st.table(comparison_df)
                        
                        # Add insight about the cost change
                        if total_updated_annual_cost > total_current_cost:
                            change_pct = ((total_updated_annual_cost - total_current_cost) / total_current_cost * 100) if total_current_cost > 0 else 0
                            st.info(f"The new annual cost represents a {change_pct:.1f}% increase from the current cost.")
                        elif total_updated_annual_cost < total_current_cost:
                            change_pct = ((total_current_cost - total_updated_annual_cost) / total_current_cost * 100) if total_current_cost > 0 else 0
                            st.success(f"The new annual cost represents a {change_pct:.1f}% decrease from the current cost.")
                        else:
                            st.info("The new annual cost is identical to the current cost.")
                
                st.markdown("### Cost Comparison")
                
                # Prepare chart data based on billing term
                if billing_term == 'Monthly':
                    # Get values from the Total Services Cost row
                    total_row = processed_data[processed_data['Cloud Service Description'] == 'Total Services Cost']
                    monthly_co_termed = float(total_row['Monthly Co-Termed Cost'].iloc[0]) if 'Monthly Co-Termed Cost' in total_row.columns else 0.0
                    first_month_co_termed = float(total_row['First Month Co-Termed Cost'].iloc[0]) if 'First Month Co-Termed Cost' in total_row.columns else 0.0
                    
                    # Current monthly cost
                    current_monthly = total_current_cost / 12
                    
                    chart_data = {
                        "currentCost": float(current_monthly),
                        "coTermedMonthly": first_month_co_termed,
                        "newMonthly": monthly_co_termed,
                        "subscription": float(total_subscription_term_fee)
                    }
                elif billing_term == 'Annual':
                    chart_data = {
                        "currentCost": float(total_current_cost),
                        "firstYearCoTerm": float(total_first_year_cost),
                        "newAnnual": float(total_updated_annual_cost),
                        "subscription": float(total_subscription_term_fee)
                    }
                elif billing_term == 'Prepaid':
                    chart_data = {
                        "currentCost": float(total_current_cost),
                        "coTermedPrepaid": float(total_prepaid_cost),
                        "subscription": float(total_subscription_term_fee)
                    }
                
                # Now generate the chart using the updated chart data
                try:
                    # Convert all values to float and ensure they're not None
                    for key in chart_data:
                        if chart_data[key] is None:
                            chart_data[key] = 0.0
                        else:
                            chart_data[key] = float(chart_data[key])
                    
                    # Render chart with safety measures
                    components.html(
                        CHART_HTML + f"""
                        <script>
                            console.log("Starting chart rendering...");
                            try {{
                                const chartData = {chart_data};
                                console.log("Chart data:", JSON.stringify(chartData));
                                renderChart(chartData, '{billing_term}', '{st.session_state.theme}');
                                console.log("Chart rendering complete");
                            }} catch (e) {{
                                console.error("Error rendering chart:", e);
                                document.write("<div style='color:red'>Error rendering chart: " + e.message + "</div>");
                            }}
                        </script>
                        """,
                        height=500
                    )
                except Exception as e:
                    st.error(f"Error generating chart: {str(e)}")
                    st.warning("Please try recalculating costs or refreshing the page.")
                
                # Generate PDF
                st.subheader("Report Generation")
                
                # Create columns for download options
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("##### PDF Report")
                    pdf_buffer = generate_pdf(
                        billing_term,
                        months_remaining,
                        extension_months,
                        total_current_cost,
                        total_prepaid_cost,
                        total_first_year_cost,
                        total_updated_annual_cost,
                        total_subscription_term_fee,
                        processed_data,
                        agreement_term,
                        customer_name,
                        customer_email,
                        account_manager,
                        company_name,
                        logo_path
                    )
                    
                    st.download_button(
                        label="Download PDF Report",
                        data=pdf_buffer,
                        file_name=f"{customer_name.replace(' ', '_')}_coterming_report.pdf" if customer_name else "coterming_report.pdf",
                        mime="application/pdf",
                        key="pdf_download"
                    )
        
        # No navigation buttons
            
    with tabs[4]:
        st.markdown('<div class="sub-header">Email Template</div>', unsafe_allow_html=True)
        
        # Check if we have calculation results
        if st.session_state.calculation_results:
            results = st.session_state.calculation_results
            total_current_cost = results["total_current_cost"]
            total_prepaid_cost = results["total_prepaid_cost"]
            total_first_year_cost = results["total_first_year_cost"]
            total_updated_annual_cost = results["total_updated_annual_cost"] 
            total_subscription_term_fee = results["total_subscription_term_fee"]
            
            # Determine which cost value to use based on billing term
            if billing_term == 'Monthly':
                first_cost = results["processed_data"][results["processed_data"]['Cloud Service Description'] == 'Total Services Cost']['First Month Co-Termed Cost'].iloc[0]
            elif billing_term == 'Annual':
                first_cost = total_first_year_cost
            else:  # Prepaid
                first_cost = total_prepaid_cost
            
            # Generate email template
            email_content = generate_email_template(
                billing_term,
                customer_name if customer_name else "[Customer Name]",
                total_current_cost,
                first_cost,
                total_subscription_term_fee,
                company_name if company_name else "[Your Company]",
                account_manager if account_manager else "[Account Manager]",
                total_updated_annual_cost
            )
            
            # Display email template with copy button
            st.markdown("### Email Template Preview")
            st.markdown('<div class="email-template">' + email_content.replace('\n', '<br>') + '</div>', unsafe_allow_html=True)
            
            # Add copy to clipboard button
            st.markdown(copy_to_clipboard_button(email_content, "Copy Email Template"), unsafe_allow_html=True)
            
            # Email subject suggestion
            st.markdown("### Suggested Email Subject")
            email_subject = f"Co-Terming Cost Proposal - {customer_name if customer_name else '[Customer Name]'}"
            st.text_input("Subject Line:", value=email_subject, key="email_subject")
            
            # Add copy button for subject line
            st.markdown(copy_to_clipboard_button(email_subject, "Copy Subject Line"), unsafe_allow_html=True)
        else:
            st.info("Please calculate costs first to generate an email template.")
        
        # No navigation buttons

elif st.session_state.active_tab == 'help_documentation':
    st.markdown('<div class="main-header">Help & Documentation</div>', unsafe_allow_html=True)
    
    # Create an accordion for different help topics
    with st.expander("How to Use This Calculator", expanded=True):
        st.markdown("""
        ### Basic Usage
        
        1. **Agreement Information**: Enter the basic details of the agreement, including billing term, agreement duration, and months remaining.
        
        2. **Customer Information**: Enter the customer details to personalize the report and email template.
        
        3. **Service Information**: Add the services that are part of the agreement, including quantities and fees.
        
        4. **Calculate Costs**: Click the 'Calculate Costs' button to generate the results.
        
        5. **Generate Reports**: After calculation, you can download a PDF report or use the generated email template.
        
        6. **Navigation**: Use the 'Next' and 'Back' buttons at the bottom of each page to move between tabs.
        """)
    
    with st.expander("Understanding Billing Terms"):
        st.markdown("""
        ### Billing Terms Explained
        
        - **Annual**: Billing occurs once per year. The calculator shows the first year co-termed cost and the updated annual cost.
        
        - **Monthly**: Billing occurs monthly. The calculator shows the first month co-termed cost and the monthly recurring cost.
        
        - **Prepaid**: The entire subscription period is paid upfront. The calculator shows the total prepaid cost.
        """)
    
    with st.expander("Calculation Methodology"):
        st.markdown("""
        ### How Costs Are Calculated
        
        - **First Month Co-Termed Cost**: For monthly billing, this represents the prorated cost for the first month based on the remaining fraction of the month.
        
        - **First Year Co-Termed Cost**: For annual billing, this represents the prorated cost for the first year based on the remaining months in the year.
        
        - **Updated Annual Cost**: This is the new annual cost after adding the additional licenses.
        
        - **Subscription Term Total Service Fee**: This is the total cost over the entire subscription period, including the extension if applicable.
        """)
    
    with st.expander("Customizing Reports and Emails"):
        st.markdown("""
        ### Customization Options
        
        - **Company Logo**: Upload your company logo in the sidebar to include it in the PDF report.
        
        - **Theme**: Switch between light and dark themes in the sidebar.
        
        - **Email Template**: The email template is automatically generated based on the calculation results and customer information. You can copy and customize it as needed.
        """)

elif st.session_state.active_tab == 'about':
    st.markdown('<div class="main-header">About This Application</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### Co-Terming Cost Calculator
    
    This application helps sales teams calculate and communicate the costs of co-terming subscription services. It supports various billing terms and provides detailed reports and email templates.
    
    ### Features
    
    - Support for Annual, Monthly, and Prepaid billing terms
    - Customizable service line items
    - Detailed cost breakdown and visualizations
    - PDF report generation
    - Email template generation
    - Light and dark themes
    - Company logo customization
    - Easy tab navigation with Next/Back buttons
    
    ### Version History
    
    - **v1.2** (Current): Added Next/Back navigation buttons for improved user experience
    - **v1.1**: Added customer information, email templates, and theme options
    - **v1.0**: Initial release with basic calculation features
    
    ### Contact
    
    For support or feature requests, please contact your application administrator.
    """)
    
    # Footer with a credit note
    st.markdown("""
    <div class="footer">
    &copy; 2024 Your Company. All rights reserved.
    </div>
    """, unsafe_allow_html=True)

# Add a footer to the main application
st.markdown("""
<div class="footer">
Co-Terming Cost Calculator v1.2 | Developed by Jim Hanus 
</div>
""", unsafe_allow_html=True)
 + value.toLocaleString();
                                }
                            }
                        },
                        x: {
                            grid: {
                                color: colors.gridColor
                            },
                            ticks: {
                                color: colors.textColor
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
    total_current_cost = 0  # Current cost before additional licenses

    for index, row in df.iterrows():
        # Calculate current costs (before additional licenses)
        current_monthly_cost = (row['Annual Unit Fee'] / 12) * row['Unit Quantity']
        current_annual_cost = row['Unit Quantity'] * row['Annual Unit Fee']
        
        # Calculate costs with additional licenses
        first_month_co_termed_cost = (row['Annual Unit Fee'] / 12) * row['Additional Licenses'] * (months_remaining % 1) if billing_term == 'Monthly' else 0
        monthly_co_termed_cost = (row['Annual Unit Fee'] / 12) * row['Additional Licenses'] if billing_term == 'Monthly' else 0
        annual_total_fee = row['Unit Quantity'] * row['Annual Unit Fee']
        subscription_term_total_fee = ((annual_total_fee * total_term) / 12) + ((row['Additional Licenses'] * row['Annual Unit Fee'] * total_term) / 12)
        co_termed_prepaid_cost = (row['Additional Licenses'] * row['Annual Unit Fee'] * total_term) / 12 if billing_term == 'Prepaid' else 0
        co_termed_first_year_cost = (row['Additional Licenses'] * row['Annual Unit Fee'] * (12 - (months_elapsed % 12))) / 12 if billing_term == 'Annual' else 0
        updated_annual_cost = annual_total_fee + (row['Additional Licenses'] * row['Annual Unit Fee']) if billing_term == 'Annual' else 0

        # Store calculated values in the dataframe based on billing term
        if billing_term == 'Monthly':
            df.at[index, 'Current Monthly Cost'] = current_monthly_cost
            df.at[index, 'First Month Co-Termed Cost'] = first_month_co_termed_cost
            df.at[index, 'Monthly Co-Termed Cost'] = monthly_co_termed_cost
        elif billing_term == 'Annual':
            df.at[index, 'Current Annual Cost'] = current_annual_cost
            df.at[index, 'First Year Co-Termed Cost'] = co_termed_first_year_cost
            df.at[index, 'Updated Annual Cost'] = updated_annual_cost
        else:  # Prepaid
            df.at[index, 'Current Annual Cost'] = current_annual_cost
            df.at[index, 'Prepaid Co-Termed Cost'] = co_termed_prepaid_cost
            
        # Always add the subscription term total
        df.at[index, 'Subscription Term Total Service Fee'] = subscription_term_total_fee

    # Convert numeric columns to float - only convert columns that exist
    numeric_cols = [
        "Annual Unit Fee", "Current Monthly Cost", "Current Annual Cost", "Prepaid Co-Termed Cost",
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
    if 'Current Annual Cost' in df.columns:
        total_current_cost = df.loc[df['Cloud Service Description'] != 'Total Services Cost', 'Current Annual Cost'].sum()
    if 'Prepaid Co-Termed Cost' in df.columns:
        total_prepaid_cost = df.loc[df['Cloud Service Description'] != 'Total Services Cost', 'Prepaid Co-Termed Cost'].sum()
    if 'First Year Co-Termed Cost' in df.columns:
        total_first_year_cost = df.loc[df['Cloud Service Description'] != 'Total Services Cost', 'First Year Co-Termed Cost'].sum()
    if 'Updated Annual Cost' in df.columns:
        total_updated_annual_cost = df.loc[df['Cloud Service Description'] != 'Total Services Cost', 'Updated Annual Cost'].sum()
    if 'Subscription Term Total Service Fee' in df.columns:
        total_subscription_term_fee = df.loc[df['Cloud Service Description'] != 'Total Services Cost', 'Subscription Term Total Service Fee'].sum()

    return df, total_current_cost, total_prepaid_cost, total_first_year_cost, total_updated_annual_cost, total_subscription_term_fee

def generate_pdf(billing_term, months_remaining, extension_months, total_current_cost, total_prepaid_cost, 
                total_first_year_cost, total_updated_annual_cost, total_subscription_term_fee, data, agreement_term, 
                customer_name="", customer_email="", account_manager="", company_name="", logo_path=None):
    pdf = FPDF(orientation='L')
    pdf.add_page()
    pdf.set_font("Arial", "B", 10)
    
    # Add logo if provided
    if logo_path and os.path.exists(logo_path):
        try:
            pdf.image(logo_path, x=10, y=10, w=50)
        except Exception as e:
            print(f"Could not add logo: {e}")
    
    # Add title
    pdf.cell(280, 8, "Co-Terming Cost Report", ln=True, align="C")
    pdf.ln(4)
    
    # Move content down to make room for logo if needed
    pdf.set_y(50)
    
    # Adjust column widths for landscape
    w_desc = 75
    w_qty = 30
    w_fee = 30
    w_lic = 30
    w_cost = 40
    w_total = 60

    # Customer Information Section
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Customer Information", ln=True, align="L")
    pdf.set_font("Arial", "", 10)
    
    pdf.cell(100, 6, f"Customer: {customer_name}", ln=False)
    pdf.cell(0, 6, f"Contact Email: {customer_email}", ln=True)
    
    pdf.cell(100, 6, f"Account Manager: {account_manager}", ln=False)
    pdf.cell(0, 6, f"Company: {company_name}", ln=True)
    
    pdf.ln(5)
    
    # Agreement Information Section
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Agreement Information", ln=True, align="L")
    pdf.set_font("Arial", "", 10)
    
    # Left side of header
    pdf.cell(100, 6, f"Date: {datetime.today().strftime('%Y-%m-%d')}", ln=False)
    pdf.cell(0, 6, f"Agreement Term: {agreement_term:.2f} months", ln=True)
    
    pdf.cell(0, 6, f"Extension Period: {extension_months} months", ln=True)
    
    pdf.cell(100, 6, f"Billing Term: {billing_term}", ln=False)
    pdf.cell(0, 6, f"Total Term: {months_remaining + extension_months:.2f} months", ln=True)
    
    pdf.ln(10)
    
    # Cost Summary Section
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Cost Summary", ln=True, align="L")
    pdf.set_font("Arial", "", 10)
    
    # Add current cost information
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 6, f"Current Annual Cost (Before Additional Licenses): ${total_current_cost:,.2f}", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.ln(5)
    
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
        pdf.cell(100, 6, "", ln=False)  # Empty left column
        pdf.cell(0, 6, f"Updated Annual Cost: ${total_updated_annual_cost:,.2f}", ln=True)
    
    pdf.ln(10)
    
    # Detailed Line Items
    pdf.set_font("Arial", "B", 7)
    pdf.cell(200, 5, "Detailed Line Items", ln=True)
    
    # Print headers
    pdf.set_font("Arial", "B", 7)
    
    # Print headers in a single row using cell method
    pdf.cell(w_desc, 6, 'Cloud Service Description', 1, 0, 'C')
    pdf.cell(w_qty, 6, 'Unit Quantity', 1, 0, 'C')
    pdf.cell(w_fee, 6, 'Annual Unit Fee', 1, 0, 'C')
    pdf.cell(w_lic, 6, 'Additional Licenses', 1, 0, 'C')
    pdf.cell(w_cost, 6, columns[-2]['title'], 1, 0, 'C')
    pdf.cell(w_total, 6, columns[-1]['title'], 1, 1, 'C')
    
    # Add a small line break
    pdf.ln(1)

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
    
    # Add footer with company information
    pdf.ln(10)
    pdf.set_font("Arial", "I", 8)
    pdf.cell(0, 6, f"Generated by {company_name}", 0, 0, 'C')

    pdf_buffer = io.BytesIO()
    pdf.output(pdf_buffer)
    pdf_buffer.seek(0)
    
    return pdf_buffer

def generate_email_template(billing_term, customer_name, current_cost, first_cost, total_subscription_cost, company_name, account_manager, updated_annual_cost=0):
    # Base template with placeholders for dynamic content
    email_templates = {
        'Monthly': f"""Dear {customer_name},

We are writing to inform you about the updated co-terming cost for your monthly billing arrangement.

Current Agreement:
- Current Annual Cost: ${current_cost:,.2f}

Updated Cost Summary:
- First Month Co-Termed Cost: ${first_cost:,.2f}
- Total Subscription Cost: ${total_subscription_cost:,.2f}
{'- Updated Annual Cost: ${updated_annual_cost:,.2f}' if updated_annual_cost > 0 else ''}

Key Details:
- The first month's co-termed cost reflects your current service adjustments.
- Your total subscription cost covers the entire term of the agreement.

Next Steps:
1. Please carefully review the cost breakdown above.
2. If you approve these terms, kindly reply to this email with your confirmation.
3. If you have any questions or concerns, please contact our sales team.

We appreciate your continued business and look forward to your approval.

Best regards,
{account_manager}
{company_name} Sales Team""",

        'Annual': f"""Dear {customer_name},

We are writing to inform you about the updated co-terming cost for your annual billing arrangement.

Current Agreement:
- Current Annual Cost: ${current_cost:,.2f}

Updated Cost Summary:
- First Year Co-Termed Cost: ${first_cost:,.2f}
- Updated Annual Cost: ${updated_annual_cost:,.2f}
- Total Subscription Cost: ${total_subscription_cost:,.2f}

Key Details:
- The first year's co-termed cost reflects your current service adjustments.
- Your total subscription cost covers the entire term of the agreement.

Next Steps:
1. Please carefully review the cost breakdown above.
2. If you approve these terms, kindly reply to this email with your confirmation.
3. If you have any questions or concerns, please contact our sales team.

We appreciate your continued business and look forward to your approval.

Best regards,
{account_manager}
{company_name} Sales Team""",

        'Prepaid': f"""Dear {customer_name},

We are writing to inform you about the updated co-terming cost for your prepaid billing arrangement.

Current Agreement:
- Current Annual Cost: ${current_cost:,.2f}

Updated Cost Summary:
- Total Pre-Paid Cost: ${first_cost:,.2f}
- Total Subscription Cost: ${total_subscription_cost:,.2f}
{'- Updated Annual Cost: ${updated_annual_cost:,.2f}' if updated_annual_cost > 0 else ''}

Key Details:
- The pre-paid cost covers your entire service term.
- Your total subscription cost reflects the full agreement period.

Next Steps:
1. Please carefully review the cost breakdown above.
2. If you approve these terms, kindly reply to this email with your confirmation.
3. If you have any questions or concerns, please contact our sales team.

We appreciate your continued business and look forward to your approval.

Best regards,
{account_manager}
{company_name} Sales Team"""
    }
    
    # Return the appropriate template based on billing term
    return email_templates.get(billing_term, "Invalid billing term")

def copy_to_clipboard_button(text, button_text="Copy to Clipboard"):
    # Create a unique key for this button
    button_id = f"copy_button_{hash(text)}"
    
    # JavaScript function to copy text to clipboard
    js_code = f"""
    <script>
    function copyToClipboard_{button_id}() {{
        const el = document.createElement('textarea');
        el.value = `{text.replace('`', '\\`')}`;
        document.body.appendChild(el);
        el.select();
        document.execCommand('copy');
        document.body.removeChild(el);
        
        // Change button text temporarily
        const btn = document.getElementById('{button_id}');
        const originalText = btn.innerHTML;
        btn.innerHTML = 'Copied!';
        setTimeout(() => {{
            btn.innerHTML = originalText;
        }}, 2000);
    }}
    </script>
    """
    
    # HTML button that calls the JavaScript function
    html_button = f"""
    {js_code}
    <button id="{button_id}" onclick="copyToClipboard_{button_id}()" 
    style="background-color: #4CAF50; color: white; padding: 10px 15px; 
    border: none; border-radius: 4px; cursor: pointer; margin-top: 10px;">
    {button_text}
    </button>
    """
    
    return html_button

# Navigation function remains for potential future use
# No navigation buttons

# Sidebar for navigation and settings
with st.sidebar:
    st.image("https://via.placeholder.com/150x50.png?text=Your+Logo", width=150)
    st.title("Navigation")
    
    # Navigation menu
    nav_options = ["Calculator", "Help & Documentation", "About"]
    nav_selection = st.radio("Go to:", nav_options)
    
    # Set the active tab based on navigation selection
    st.session_state.active_tab = nav_selection.lower().replace(" & ", "_").replace(" ", "_")
    
    st.markdown("---")
    
    # Theme toggle
    st.subheader("Settings")
    theme_options = ["Light", "Dark"]
    selected_theme = st.radio("Theme:", theme_options, index=0 if st.session_state.theme == 'light' else 1)
    st.session_state.theme = selected_theme.lower()
    
    st.markdown("---")
    
    # Uploader for logo
    st.subheader("Company Logo")
    uploaded_logo = st.file_uploader("Upload your logo for PDF reports", type=["png", "jpg", "jpeg"])
    if uploaded_logo:
        # Save the uploaded file
        logo_path = "logo.png"
        with open(logo_path, "wb") as f:
            f.write(uploaded_logo.getbuffer())
        st.success("Logo uploaded successfully!")
    else:
        logo_path = None
    
    st.markdown("---")
    
    # App info
    st.markdown("##### Co-Terming Calculator v1.1")
    st.markdown("© 2024 Your Company")

# Main content area
if st.session_state.active_tab in ['calculator', 'results']:
    # Custom HTML header
    st.markdown('<div class="main-header">Co-Terming Cost Calculator</div>', unsafe_allow_html=True)
    
    # Create tabs for different sections of the calculator
    tab_titles = ["Agreement Info", "Customer Info", "Services", "Results", "Email Template"]
    
    # Set the active tab based on session state
    active_tab_index = st.session_state.current_tab
    tabs = st.tabs(tab_titles)
    
    with tabs[0]:
        st.markdown('<div class="sub-header">Agreement Information</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            current_date = datetime.today().strftime('%Y-%m-%d')
            st.text(f"Current Date: {current_date}")
            billing_term = st.selectbox("Billing Term:", ["Annual", "Prepaid", "Monthly"])
            # Add date picker for agreement start date
            agreement_start_date = st.date_input("Agreement Start Date:", 
                                               value=date.today() - relativedelta(months=6),
                                               max_value=date.today())
        
        with col2:
            agreement_term = st.number_input("Agreement Term (Months):", min_value=1, value=36, step=1, format="%d")
            
            # Calculate months remaining based on start date and agreement term with day precision
            today = date.today()
            
            # Calculate full months passed
            months_passed = relativedelta(today, agreement_start_date).years * 12 + relativedelta(today, agreement_start_date).months
            
            # Calculate the day fraction of the current month
            # Get days in the current month
            if today.month == 12:
                last_day_of_month = date(today.year + 1, 1, 1) - relativedelta(days=1)
            else:
                last_day_of_month = date(today.year, today.month + 1, 1) - relativedelta(days=1)
            
            days_in_month = last_day_of_month.day
            day_fraction = (days_in_month - today.day) / days_in_month
            
            # Add the day fraction to get precise months passed
            precise_months_passed = months_passed + (1 - day_fraction)
            
            # Calculate remaining months with precision
            calculated_months_remaining = max(0, agreement_term - precise_months_passed)
            
            # Display calculated months remaining with 2 decimal precision
            st.text(f"Calculated Months Remaining: {calculated_months_remaining:.2f}")
            
            # Allow manual override of months remaining
            months_remaining = st.number_input("Override Months Remaining (if needed):", 
                                             min_value=0.0, 
                                             max_value=float(agreement_term), 
                                             value=float(calculated_months_remaining), 
                                             step=0.01, 
                                             format="%.2f")
        
        # Add extension period option
        add_extension = st.checkbox("Add Agreement Extension?")
        if add_extension:
            extension_months = st.number_input("Extension Period (Months):", min_value=1, value=12, step=1, format="%d")
            total_term = months_remaining + extension_months
            st.info(f"Total Term: {total_term:.2f} months")
        else:
            extension_months = 0
            total_term = months_remaining
        
        # No navigation buttons
            
    with tabs[1]:
        st.markdown('<div class="sub-header">Customer Information</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            customer_name = st.text_input("Customer Name:", placeholder="Enter customer name")
            customer_email = st.text_input("Customer Email:", placeholder="Enter customer email")
        
        with col2:
            account_manager = st.text_input("Account Manager:", placeholder="Enter account manager name")
            company_name = st.text_input("Your Company:", value="Your Company Name", placeholder="Enter your company name")
        
        # No navigation buttons
            
    with tabs[2]:
        st.markdown('<div class="sub-header">Service Information</div>', unsafe_allow_html=True)
        
        num_items = st.number_input("Number of Line Items:", min_value=1, value=1, step=1, format="%d")
        
        columns = ["Cloud Service Description", "Unit Quantity", "Annual Unit Fee", "Additional Licenses", 
                  "Prepaid Co-Termed Cost", "First Year Co-Termed Cost", "Updated Annual Cost", 
                  "Subscription Term Total Service Fee", "Monthly Co-Termed Cost", "First Month Co-Termed Cost"]
        data = pd.DataFrame(columns=columns)
        
        # Define numeric columns for proper handling
        numeric_cols = [
            "Annual Unit Fee", "Current Monthly Cost", "Current Annual Cost", "Prepaid Co-Termed Cost",
            "First Year Co-Termed Cost", "Updated Annual Cost", "Subscription Term Total Service Fee",
            "Monthly Co-Termed Cost", "First Month Co-Termed Cost"
        ]
        
        # Create a container for the line items
        line_items_container = st.container()
        
        with line_items_container:
            for i in range(num_items):
                st.markdown(f"**Item {i+1}**")
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                
                # Use a unique key for each input to avoid conflicts
                service_key = f"service_{i}"
                qty_key = f"qty_{i}"
                fee_key = f"fee_{i}"
                add_lic_key = f"add_lic_{i}"
                
                        # Create input fields for each row
                service = col1.text_input("Service Description", key=service_key, placeholder="Enter service name")
                qty = col2.number_input("Quantity", min_value=0, value=1, step=1, format="%d", key=qty_key)
                fee = col3.number_input("Annual Fee ($)", min_value=0.0, value=1000.0, step=100.0, format="%.2f", key=fee_key)
                add_lic = col4.number_input("Add. Licenses", min_value=0, value=0, step=1, format="%d", key=add_lic_key)
                
                # Add the row data to our dataframe
                row_data = {
                    "Cloud Service Description": service if service else "",
                    "Unit Quantity": qty,
                    "Annual Unit Fee": fee,
                    "Additional Licenses": add_lic,
                }
                
                # Fill in missing columns with empty values or zeros
                for col in columns:
                    if col not in row_data:
                        row_data[col] = 0 if col in numeric_cols else ""
                        
                # Append to the dataframe
                new_row = pd.DataFrame([row_data])
                data = pd.concat([data, new_row], ignore_index=True)
        
        # Add validation for empty service descriptions
        empty_services = data["Cloud Service Description"].isnull() | (data["Cloud Service Description"] == "")
        if empty_services.any():
            st.warning("⚠️ Please enter a description for all services.")
        
        # Store service data in session state
        st.session_state.service_data = data
        
        # No navigation buttons
            
    with tabs[3]:
        st.markdown('<div class="sub-header">Results</div>', unsafe_allow_html=True)
        
        # Check if we have service data in session state from the Services tab
        if 'service_data' in st.session_state:
            data = st.session_state.service_data
            valid_data = True
        else:
            # Check if we have valid data before calculating
            valid_data = not empty_services.any() and len(data) > 0
        
        # Create a placeholder for calculation results
        results_placeholder = st.empty()
        
        # Calculate button on the results page
        calculate_button = st.button("Calculate Costs", disabled=not valid_data, 
                                     help="Enter all required information to enable calculations")
        
        # Store calculation results in session state
        if "calculation_results" not in st.session_state:
            st.session_state.calculation_results = None
            
        if calculate_button and valid_data:
            with st.spinner("Calculating costs..."):
                # Calculate costs
                processed_data, total_current_cost, total_prepaid_cost, total_first_year_cost, total_updated_annual_cost, total_subscription_term_fee = calculate_costs(
                    data,
                    agreement_term,
                    months_remaining,
                    extension_months,
                    billing_term
                )
                
                # Store results in session state
                st.session_state.calculation_results = {
                    "processed_data": processed_data,
                    "total_current_cost": total_current_cost,
                    "total_prepaid_cost": total_prepaid_cost,
                    "total_first_year_cost": total_first_year_cost,
                    "total_updated_annual_cost": total_updated_annual_cost,
                    "total_subscription_term_fee": total_subscription_term_fee
                }
                
            st.success("Calculations completed successfully!")
            
        # Display results if available
        if st.session_state.calculation_results:
            results = st.session_state.calculation_results
            processed_data = results["processed_data"]
            total_current_cost = results["total_current_cost"]
            total_prepaid_cost = results["total_prepaid_cost"]
            total_first_year_cost = results["total_first_year_cost"]
            total_updated_annual_cost = results["total_updated_annual_cost"]
            total_subscription_term_fee = results["total_subscription_term_fee"]
            
            with results_placeholder.container():
                st.subheader("Detailed Line Items")
                
                # Handle column dropping more thoroughly
                columns_to_drop = []
                if billing_term == 'Monthly':
                    columns_to_drop = ['Prepaid Co-Termed Cost', 'First Year Co-Termed Cost', 'Updated Annual Cost', 'Current Annual Cost']
                elif billing_term == 'Annual':
                    columns_to_drop = ['Prepaid Co-Termed Cost', 'Monthly Co-Termed Cost', 'First Month Co-Termed Cost', 'Current Monthly Cost']
                elif billing_term == 'Prepaid':
                    columns_to_drop = ['Monthly Co-Termed Cost', 'First Month Co-Termed Cost', 'First Year Co-Termed Cost', 'Updated Annual Cost', 'Current Monthly Cost']
                
                # Only drop columns that exist in the dataframe
                displayed_data = processed_data.copy()
                existing_columns_to_drop = [col for col in columns_to_drop if col in displayed_data.columns]
                if existing_columns_to_drop:
                    displayed_data = displayed_data.drop(columns=existing_columns_to_drop)
                
                # Format numeric columns
                for col in ["Annual Unit Fee", "Prepaid Co-Termed Cost", "First Year Co-Termed Cost", 
                            "Updated Annual Cost", "Subscription Term Total Service Fee", 
                            "Monthly Co-Termed Cost", "First Month Co-Termed Cost"]:
                    if col in displayed_data.columns:
                        displayed_data[col] = pd.to_numeric(displayed_data[col], errors='coerce')
                
                # Display the dataframe with formatting
                st.dataframe(displayed_data.style.format({
                    "Annual Unit Fee": "${:,.2f}",
                    "Prepaid Co-Termed Cost": "${:,.2f}",
                    "First Year Co-Termed Cost": "${:,.2f}",
                    "Updated Annual Cost": "${:,.2f}",
                    "Subscription Term Total Service Fee": "${:,.2f}",
                    "Monthly Co-Termed Cost": "${:,.2f}",
                    "First Month Co-Termed Cost": "${:,.2f}"
                }).set_properties(**{"white-space": "normal"}))
                
                # Show current cost summary based on billing term
                st.markdown("### Current Agreement Cost")
                
                if billing_term == 'Monthly':
                    # Show only monthly cost for Monthly billing term
                    current_monthly = total_current_cost / 12
                    st.markdown(f"**Current Monthly Cost:** ${current_monthly:,.2f}")
                else:
                    # Show only annual cost for Annual and Prepaid billing terms
                    st.markdown(f"**Current Annual Cost:** ${total_current_cost:,.2f}")
                
                # Calculate total licenses (current + additional)
                total_current_licenses = processed_data[processed_data['Cloud Service Description'] != 'Total Services Cost']['Unit Quantity'].sum()
                total_additional_licenses = processed_data[processed_data['Cloud Service Description'] != 'Total Services Cost']['Additional Licenses'].sum()
                total_licenses = total_current_licenses + total_additional_licenses
                
                # Display license summary
                st.markdown("### License Summary")
                license_data = {
                    "License Type": ["Current Licenses", "Additional Licenses", "Total Licenses"],
                    "Count": [
                        f"{int(total_current_licenses)}",
                        f"{int(total_additional_licenses)}",
                        f"{int(total_licenses)}"
                    ]
                }
                
                license_df = pd.DataFrame(license_data)
                st.table(license_df)
                
                if total_additional_licenses > 0:
                    increase_pct = (total_additional_licenses / total_current_licenses * 100) if total_current_licenses > 0 else 0
                    st.info(f"You're adding {int(total_additional_licenses)} licenses ({increase_pct:.1f}% increase).")
                
                with st.expander("Current vs. New Cost Summary", expanded=True):
                    # Create a comparison table with billing term-specific labels
                    if billing_term == 'Monthly':
                        current_cost_monthly = total_current_cost / 12
                        new_cost_monthly = total_updated_annual_cost / 12
                        
                        comparison_data = {
                            "Cost Type": ["Current Monthly Cost", "New Monthly Cost", "Difference", "Percentage Change"],
                            "Amount": [
                                f"${current_cost_monthly:,.2f}",
                                f"${new_cost_monthly:,.2f}",
                                f"${new_cost_monthly - current_cost_monthly:,.2f}",
                                f"{((new_cost_monthly - current_cost_monthly) / current_cost_monthly * 100) if current_cost_monthly > 0 else 0:,.2f}%"
                            ]
                        }
                        
                        comparison_df = pd.DataFrame(comparison_data)
                        st.table(comparison_df)
                        
                        # Add insight about the cost change
                        if new_cost_monthly > current_cost_monthly:
                            change_pct = ((new_cost_monthly - current_cost_monthly) / current_cost_monthly * 100) if current_cost_monthly > 0 else 0
                            st.info(f"The new monthly cost represents a {change_pct:.1f}% increase from the current cost.")
                        elif new_cost_monthly < current_cost_monthly:
                            change_pct = ((current_cost_monthly - new_cost_monthly) / current_cost_monthly * 100) if current_cost_monthly > 0 else 0
                            st.success(f"The new monthly cost represents a {change_pct:.1f}% decrease from the current cost.")
                        else:
                            st.info("The new monthly cost is identical to the current cost.")
                    else:
                        # For Annual and Prepaid, show annual costs
                        comparison_data = {
                            "Cost Type": ["Current Annual Cost", "New Annual Cost", "Difference", "Percentage Change"],
                            "Amount": [
                                f"${total_current_cost:,.2f}",
                                f"${total_updated_annual_cost:,.2f}",
                                f"${total_updated_annual_cost - total_current_cost:,.2f}",
                                f"{((total_updated_annual_cost - total_current_cost) / total_current_cost * 100) if total_current_cost > 0 else 0:,.2f}%"
                            ]
                        }
                        
                        comparison_df = pd.DataFrame(comparison_data)
                        st.table(comparison_df)
                        
                        # Add insight about the cost change
                        if total_updated_annual_cost > total_current_cost:
                            change_pct = ((total_updated_annual_cost - total_current_cost) / total_current_cost * 100) if total_current_cost > 0 else 0
                            st.info(f"The new annual cost represents a {change_pct:.1f}% increase from the current cost.")
                        elif total_updated_annual_cost < total_current_cost:
                            change_pct = ((total_current_cost - total_updated_annual_cost) / total_current_cost * 100) if total_current_cost > 0 else 0
                            st.success(f"The new annual cost represents a {change_pct:.1f}% decrease from the current cost.")
                        else:
                            st.info("The new annual cost is identical to the current cost.")
                
                st.markdown("### Cost Comparison")
                
                # Prepare chart data based on billing term
                if billing_term == 'Monthly':
                    # Get values from the Total Services Cost row
                    total_row = processed_data[processed_data['Cloud Service Description'] == 'Total Services Cost']
                    monthly_co_termed = float(total_row['Monthly Co-Termed Cost'].iloc[0]) if 'Monthly Co-Termed Cost' in total_row.columns else 0.0
                    first_month_co_termed = float(total_row['First Month Co-Termed Cost'].iloc[0]) if 'First Month Co-Termed Cost' in total_row.columns else 0.0
                    
                    # Current monthly cost
                    current_monthly = total_current_cost / 12
                    
                    chart_data = {
                        "currentCost": float(current_monthly),
                        "coTermedMonthly": first_month_co_termed,
                        "newMonthly": monthly_co_termed,
                        "subscription": float(total_subscription_term_fee)
                    }
                elif billing_term == 'Annual':
                    chart_data = {
                        "currentCost": float(total_current_cost),
                        "firstYearCoTerm": float(total_first_year_cost),
                        "newAnnual": float(total_updated_annual_cost),
                        "subscription": float(total_subscription_term_fee)
                    }
                elif billing_term == 'Prepaid':
                    chart_data = {
                        "currentCost": float(total_current_cost),
                        "coTermedPrepaid": float(total_prepaid_cost),
                        "subscription": float(total_subscription_term_fee)
                    }
                
                # Now generate the chart using the updated chart data
                try:
                    # Convert all values to float and ensure they're not None
                    for key in chart_data:
                        if chart_data[key] is None:
                            chart_data[key] = 0.0
                        else:
                            chart_data[key] = float(chart_data[key])
                    
                    # Render chart with safety measures
                    components.html(
                        CHART_HTML + f"""
                        <script>
                            console.log("Starting chart rendering...");
                            try {{
                                const chartData = {chart_data};
                                console.log("Chart data:", JSON.stringify(chartData));
                                renderChart(chartData, '{billing_term}', '{st.session_state.theme}');
                                console.log("Chart rendering complete");
                            }} catch (e) {{
                                console.error("Error rendering chart:", e);
                                document.write("<div style='color:red'>Error rendering chart: " + e.message + "</div>");
                            }}
                        </script>
                        """,
                        height=500
                    )
                except Exception as e:
                    st.error(f"Error generating chart: {str(e)}")
                    st.warning("Please try recalculating costs or refreshing the page.")
                
                # Generate PDF
                st.subheader("Report Generation")
                
                # Create columns for download options
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("##### PDF Report")
                    pdf_buffer = generate_pdf(
                        billing_term,
                        months_remaining,
                        extension_months,
                        total_current_cost,
                        total_prepaid_cost,
                        total_first_year_cost,
                        total_updated_annual_cost,
                        total_subscription_term_fee,
                        processed_data,
                        agreement_term,
                        customer_name,
                        customer_email,
                        account_manager,
                        company_name,
                        logo_path
                    )
                    
                    st.download_button(
                        label="Download PDF Report",
                        data=pdf_buffer,
                        file_name=f"{customer_name.replace(' ', '_')}_coterming_report.pdf" if customer_name else "coterming_report.pdf",
                        mime="application/pdf",
                        key="pdf_download"
                    )
        
        # No navigation buttons
            
    with tabs[4]:
        st.markdown('<div class="sub-header">Email Template</div>', unsafe_allow_html=True)
        
        # Check if we have calculation results
        if st.session_state.calculation_results:
            results = st.session_state.calculation_results
            total_current_cost = results["total_current_cost"]
            total_prepaid_cost = results["total_prepaid_cost"]
            total_first_year_cost = results["total_first_year_cost"]
            total_updated_annual_cost = results["total_updated_annual_cost"] 
            total_subscription_term_fee = results["total_subscription_term_fee"]
            
            # Determine which cost value to use based on billing term
            if billing_term == 'Monthly':
                first_cost = results["processed_data"][results["processed_data"]['Cloud Service Description'] == 'Total Services Cost']['First Month Co-Termed Cost'].iloc[0]
            elif billing_term == 'Annual':
                first_cost = total_first_year_cost
            else:  # Prepaid
                first_cost = total_prepaid_cost
            
            # Generate email template
            email_content = generate_email_template(
                billing_term,
                customer_name if customer_name else "[Customer Name]",
                total_current_cost,
                first_cost,
                total_subscription_term_fee,
                company_name if company_name else "[Your Company]",
                account_manager if account_manager else "[Account Manager]",
                total_updated_annual_cost
            )
            
            # Display email template with copy button
            st.markdown("### Email Template Preview")
            st.markdown('<div class="email-template">' + email_content.replace('\n', '<br>') + '</div>', unsafe_allow_html=True)
            
            # Add copy to clipboard button
            st.markdown(copy_to_clipboard_button(email_content, "Copy Email Template"), unsafe_allow_html=True)
            
            # Email subject suggestion
            st.markdown("### Suggested Email Subject")
            email_subject = f"Co-Terming Cost Proposal - {customer_name if customer_name else '[Customer Name]'}"
            st.text_input("Subject Line:", value=email_subject, key="email_subject")
            
            # Add copy button for subject line
            st.markdown(copy_to_clipboard_button(email_subject, "Copy Subject Line"), unsafe_allow_html=True)
        else:
            st.info("Please calculate costs first to generate an email template.")
        
        # No navigation buttons

elif st.session_state.active_tab == 'help_documentation':
    st.markdown('<div class="main-header">Help & Documentation</div>', unsafe_allow_html=True)
    
    # Create an accordion for different help topics
    with st.expander("How to Use This Calculator", expanded=True):
        st.markdown("""
        ### Basic Usage
        
        1. **Agreement Information**: Enter the basic details of the agreement, including billing term, agreement duration, and months remaining.
        
        2. **Customer Information**: Enter the customer details to personalize the report and email template.
        
        3. **Service Information**: Add the services that are part of the agreement, including quantities and fees.
        
        4. **Calculate Costs**: Click the 'Calculate Costs' button to generate the results.
        
        5. **Generate Reports**: After calculation, you can download a PDF report or use the generated email template.
        
        6. **Navigation**: Use the 'Next' and 'Back' buttons at the bottom of each page to move between tabs.
        """)
    
    with st.expander("Understanding Billing Terms"):
        st.markdown("""
        ### Billing Terms Explained
        
        - **Annual**: Billing occurs once per year. The calculator shows the first year co-termed cost and the updated annual cost.
        
        - **Monthly**: Billing occurs monthly. The calculator shows the first month co-termed cost and the monthly recurring cost.
        
        - **Prepaid**: The entire subscription period is paid upfront. The calculator shows the total prepaid cost.
        """)
    
    with st.expander("Calculation Methodology"):
        st.markdown("""
        ### How Costs Are Calculated
        
        - **First Month Co-Termed Cost**: For monthly billing, this represents the prorated cost for the first month based on the remaining fraction of the month.
        
        - **First Year Co-Termed Cost**: For annual billing, this represents the prorated cost for the first year based on the remaining months in the year.
        
        - **Updated Annual Cost**: This is the new annual cost after adding the additional licenses.
        
        - **Subscription Term Total Service Fee**: This is the total cost over the entire subscription period, including the extension if applicable.
        """)
    
    with st.expander("Customizing Reports and Emails"):
        st.markdown("""
        ### Customization Options
        
        - **Company Logo**: Upload your company logo in the sidebar to include it in the PDF report.
        
        - **Theme**: Switch between light and dark themes in the sidebar.
        
        - **Email Template**: The email template is automatically generated based on the calculation results and customer information. You can copy and customize it as needed.
        """)

elif st.session_state.active_tab == 'about':
    st.markdown('<div class="main-header">About This Application</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### Co-Terming Cost Calculator
    
    This application helps sales teams calculate and communicate the costs of co-terming subscription services. It supports various billing terms and provides detailed reports and email templates.
    
    ### Features
    
    - Support for Annual, Monthly, and Prepaid billing terms
    - Customizable service line items
    - Detailed cost breakdown and visualizations
    - PDF report generation
    - Email template generation
    - Light and dark themes
    - Company logo customization
    - Easy tab navigation with Next/Back buttons
    
    ### Version History
    
    - **v1.2** (Current): Added Next/Back navigation buttons for improved user experience
    - **v1.1**: Added customer information, email templates, and theme options
    - **v1.0**: Initial release with basic calculation features
    
    ### Contact
    
    For support or feature requests, please contact your application administrator.
    """)
    
    # Footer with a credit note
    st.markdown("""
    <div class="footer">
    © 2024 Your Company. All rights reserved.
    </div>
    """, unsafe_allow_html=True)

# Add a footer to the main application
st.markdown("""
<div class="footer">
Co-Terming Cost Calculator v1.2 | Developed by Your Team
</div>
""", unsafe_allow_html=True)
