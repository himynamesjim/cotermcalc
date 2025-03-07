import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
from fpdf import FPDF
import streamlit.components.v1 as components
import base64
import io
import os

def conditional_round(value, threshold=0.25):
    """Rounds values close to whole numbers based on a threshold."""
    if abs(value - round(value)) < threshold:
        return round(value)
    return round(value, 2)  # Keep two decimal places otherwise

# Set page configuration and theme options
st.set_page_config(
    page_title="Co-Terming Cost Calculator",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)
# Force dark mode
st.session_state.theme = 'dark'

st.markdown("""
<style>
    :root {
        --background-color: rgb(51, 51, 51);
        --text-color: rgb(255, 255, 255);
        
        /* Dark theme styling */
        color-scheme: dark;
    }
 
     /* Style the tooltip/popup for help text */
    [data-baseweb="tooltip"],
    [role="tooltip"],
    .stTooltipContent {
        background-color: #2e3440 !important;
        color: #d8dee9 !important;
        border: 1px solid #4c566a !important;
        border-radius: 4px !important;
        padding: 8px 12px !important;
        font-size: 14px !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3) !important;
        max-width: 400px !important;
        z-index: 1000 !important;
    }
    
    /* Style the tooltip arrow if needed */
    [data-baseweb="tooltip"]::after,
    [role="tooltip"]::after,
    .stTooltipContent::after {
        border-color: #2e3440 !important;
    }
    /* Target all action buttons including Calculate Results */
    .stButton>button, 
    [data-testid="baseButton-secondary"], 
    .st-emotion-cache-ocsh0s.e1ewe7hr3,
    .st-emotion-cache-ocsh0s,            /* Add general class */
    button[kind="primary"],              /* Add primary buttons */
    button[kind="secondary"],            /* Add secondary buttons */
    button[data-testid="StyledButton"],  /* Add styled buttons */
    .element-container button,           /* Catch buttons in containers */
    form button {                        /* Catch form buttons */
        background-color: #2e3440 !important;  /* Dark Nord theme background */
        color: #d8dee9 !important;             /* Light gray text */
        border: 1px solid #4c566a !important;  /* Subtle border */
        border-radius: 4px !important;
        transition: all 0.2s ease !important;
    }
    
  /* Also apply hover styles to all the above button types */
    .stButton>button:hover, 
    [data-testid="baseButton-secondary"]:hover, 
    .st-emotion-cache-ocsh0s.e1ewe7hr3:hover,
    .st-emotion-cache-ocsh0s:hover,
    button[kind="primary"]:hover,
    button[kind="secondary"]:hover,
    button[data-testid="StyledButton"]:hover,
    .element-container button:hover,
    form button:hover {
        background-color: #4c566a !important;  /* Lighter dark color on hover */
        border-color: #81a1c1 !important;      /* Blue-ish border on hover */
        box-shadow: 0 0 5px rgba(129, 161, 193, 0.5) !important; /* Subtle glow */
    }
    
    /* Active/clicked state */
    .stButton>button:active, [data-testid="baseButton-secondary"]:active, .st-emotion-cache-ocsh0s.e1ewe7hr3:active {
        background-color: #3b4252 !important;  /* Mid-dark color when clicked */
        transform: translateY(1px) !important; /* Subtle push effect */
    }
    
    /* Disabled state */
    .stButton>button:disabled, [data-testid="baseButton-secondary"]:disabled, .st-emotion-cache-ocsh0s.e1ewe7hr3:disabled {
        background-color: #2e3440 !important;  /* Same as normal but more muted */
        color: #4c566a !important;             /* Darker text for disabled state */
        border-color: #3b4252 !important;
        opacity: 0.7 !important;
        cursor: not-allowed !important;
    }
    
    /* Download button specific styling if needed */
    .stDownloadButton>button {
        background-color: #2e3440 !important;
        color: #d8dee9 !important;
        border: 1px solid #4c566a !important;
    }
    
    .stDownloadButton>button:hover {
        background-color: #4c566a !important;
        border-color: #81a1c1 !important;
    }
    
    /* Ensure button text is always properly colored */
    .stButton>button *, .stDownloadButton>button * {
        color: #d8dee9 !important;
    }
    
    /* Leave navigation buttons with default styling */
    [data-testid="stSidebarNavItems"] button,
    [data-testid="stSidebarNav"] button,
    .stRadio button {
        background-color: inherit;
        border-color: inherit;
    }
    
    /* Target the specific button class for Calculate and other action buttons */
    .st-emotion-cache-ocsh0s.e1ewe7hr3 {
        background-color: #4b8bbe !important;
        color: white !important;
        border-color: #366b99 !important;
    }
    
    /* Leave navigation buttons with their default styling */
    [data-testid="stSidebarNavItems"] button,
    [data-testid="stSidebarNav"] button,
    .stRadio button {
        background-color: inherit;
        border-color: inherit;
    }
    
    /* Ensure button text is colored appropriately */
    .stButton>button *, [data-testid="baseButton-secondary"] * {
        color: white !important;
    }
    
    /* Button hover state */
    .stButton > button:hover {
        background-color: #366b99 !important;
        border-color: #264d73 !important;
    }
    
    /* Button active/clicked state */
    .stButton > button:active {
        background-color: #264d73 !important;
    }
    
    /* Disabled button state */
    .stButton > button:disabled {
        background-color: #2c3e50 !important;
        color: #95a5a6 !important;
        border-color: #2c3e50 !important;
        opacity: 0.7 !important;
    }
    
    /* Fix form container backgrounds */
    div[data-testid="stForm"] {
        background-color: #262730 !important;
    }
    
    /* Fix tooltip and helper text */
    div[data-baseweb="tooltip"] {
        background-color: #262730 !important;
        color: #ffffff !important;
    }
        /* Make all paragraph and text elements white */
    p, span, label, li, td, div, 
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] span,
    .stMarkdown, .stText {
        color: #ffffff !important;
    }
    /* Also target specific Streamlit text classes */
    .st-emotion-cache-ue6h4q, .st-emotion-cache-nahz7x, 
    .st-emotion-cache-10trblm, .st-emotion-cache-1gulkj5,
    .st-emotion-cache-1avcm0n {
        color: #ffffff !important;
    }
    
    /* And any customizable elements that might contain text */
    .streamlit-expanderHeader, .stTabs [role="tab"], .stRadio label {
        color: #ffffff !important;
    }
    
    /* Make sure form labels are white too */
    .stNumberInput label, .stTextInput label, .stDateInput label, 
    .stTimeInput label, .stSelectbox label, .stMultiselect label {
        color: #ffffff !important;
    }
    
    /* Main background */
    .stApp {
        background-color: rgb(14, 17, 23) !important; 
        color: rgb(250, 250, 250) !important;
    }
    
    /* Sidebar background */
    [data-testid="stSidebar"] {
        background-color: rgb(14, 17, 23) !important;
    }
    
    /* All inputs, widgets, and controls */
    input, textarea, [role="listbox"], [data-baseweb="input"], [data-baseweb="select"] {
        background-color: rgb(33, 37, 41) !important;
        color: rgb(255, 255, 255) !important;
    }
    
    /* Ensure dark mode persists */
    .st-emotion-cache-lrlib {
        color: rgb(250, 250, 250) !important;
    }
</style>
""", unsafe_allow_html=True)
    
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 'calculator'


# Add this CSS to your local_css function
def local_css():
    # Always use dark mode regardless of session state
    bg_color = "#0e1117"
    text_color = "#ffffff"
    accent_color = "#4b8bbe"
    secondary_bg = "#000000"
    input_bg = "#1e1e1e"
    border_color = "rgba(255, 255, 255, 0.1)"
    info_bg = "rgba(75, 139, 190, 0.15)"
    total_bg = "rgba(65, 105, 225, 0.15)"
    
    return f"""
    <style>
    /* Original styles */
    /* Force dark theme - essential overrides */
    .stApp, 
    .main, 
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="baseButton-headerNoPadding"],
    [data-testid="stSidebar"] {{
        background-color: {bg_color} !important;
        color: {text_color} !important;
    }}
    
    /* Force inputs to use dark theme */
    input, 
    textarea, 
    [data-baseweb="select"] > div,
    [data-baseweb="input"] > div {{
        background-color: {input_bg} !important;
        color: {text_color} !important;
        border-color: {border_color} !important;
    }}
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
        border-top: 1px solid {border_color};
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
    
    
    /* New styles for form elements */
    /* Standardize input field heights */
    div.stDateInput > div[data-baseweb="input"] > div,
    div.stSelectbox > div > div[data-baseweb="select"] > div,
    div.stNumberInput > div > div[data-baseweb="input"] > div {{
        height: 40px !important;
        background-color: {input_bg} !important;
        border-radius: 4px !important;
        border: 1px solid {border_color} !important;
    }}
    
    /* Style number input buttons */
    div.stNumberInput div[data-baseweb="input"] button {{
        background-color: transparent !important;
        border: none !important;
    }}
    
    /* Add consistent spacing */
    div.stDateInput, div.stNumberInput, div.stSelectbox {{
        margin-bottom: 1rem !important;
    }}
    
    /* Field labels */
    .field-label {{
        font-size: 0.9rem;
        font-weight: 500;
        color: {text_color};
        margin-bottom: 0.3rem;
        margin-top: 0.7rem;
    }}
    
    /* Info display boxes */
    .info-display {{
        background-color: {secondary_bg};
        border-left: 3px solid {accent_color};
        border-radius: 4px;
        padding: 0.8rem;
        margin-top: 0.5rem;
        margin-bottom: 1rem;
    }}
    
    .total-display {{
        background-color: {total_bg};
        border-left: 3px solid {accent_color};
        border-radius: 4px;
        padding: 0.8rem;
        margin-top: 0.5rem;
    }}
    
    .info-label {{
        font-weight: 600;
    }}
    
    /* Section divider */
    .section-divider {{
        height: 1px;
        background-color: {border_color};
        margin: 1.5rem 0;
    }}
    
    /* Fix checkbox alignment */
    .stCheckbox > div {{
        display: flex !important;
        align-items: center !important;
    }}
    </style>
    """

# Apply CSS
st.markdown(local_css(), unsafe_allow_html=True)

# Chart HTML/JS with dynamic theme support - FIXED VERSION
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
            
            let datasets = [];
            
            if (billingTerm === 'Annual') {
                datasets = [
                    {
                        label: 'First Year Co-Termed Cost',
                        data: [data.firstYearCoTerm || 0],
                        backgroundColor: colors.barColors[1]
                    },
                    {
                        label: 'Current Annual Cost',
                        data: [data.currentCost || 0],
                        backgroundColor: colors.barColors[0]
                    },
                    {
                        label: 'Updated Annual Cost',
                        data: [data.newAnnual || 0],
                        backgroundColor: colors.barColors[2]
                    },
                    {
                        label: 'Remaining Total Subscription Cost',
                        data: [data.subscription || 0],
                        backgroundColor: '#ff7f50'  // Coral color for total subscription
                    }
                ];
            }
          else if (billingTerm === 'Monthly') {
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
                        label: 'New Monthly Cost',
                        data: [data.newMonthly || 0],
                        backgroundColor: colors.barColors[2]
                    },
                    {
                        label: 'Remaining Total Subscription Cost',
                        data: [data.subscription || 0],
                        backgroundColor: '#ff7f50'
                    }
                ];
            }
            else if (billingTerm === 'Prepaid') {
                datasets = [
                    {
                        label: 'Current Prepaid Cost (Remaining Months)',
                        data: [data.currentCost || 0],
                        backgroundColor: colors.barColors[0]
                    },
                    {
                        label: 'Additional Licenses Prepaid Cost',
                        data: [data.coTermedPrepaid || 0],
                        backgroundColor: colors.barColors[1]
                    },
                    {
                        label: 'Remaining Total Subscription Cost',
                        data: [data.subscription || 0],
                        backgroundColor: '#ff7f50'
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
                                return '$' + value.toLocaleString(undefined, {
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
                                    return '$' + value.toLocaleString();
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
# Add this function after the existing imports
def calculate_co_termed_months_remaining(co_termed_start_date, agreement_start_date, agreement_term):
    """
    Calculates months remaining based on the co-termed start date and agreement term.
    """
    # Convert dates to pandas Timestamps for compatibility
    co_termed_start_date = pd.Timestamp(co_termed_start_date)
    agreement_start_date = pd.Timestamp(agreement_start_date)

    # ✅ Calculate the agreement's original end date
    agreement_end_date = agreement_start_date + pd.DateOffset(months=agreement_term)

    # ✅ Calculate months remaining from the Co-Term Start Date to the Agreement End Date
    days_remaining = (agreement_end_date - co_termed_start_date).days
    months_remaining = days_remaining / 30.44  # Convert days to months

    return max(round(months_remaining, 2), 0)  # Prevents negative values





def calculate_costs(df, agreement_term, months_remaining, extension_months, billing_term):
    total_term = months_remaining + extension_months
    months_elapsed = agreement_term - months_remaining
    
    # Convert relevant columns to numeric, but exclude "Cloud Service Description"
    for col in df.select_dtypes(include=['object']).columns:
        if col != "Cloud Service Description":  # ✅ Prevent license names from becoming numbers
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Ensure "Cloud Service Description" is explicitly kept as text
    df["Cloud Service Description"] = df["Cloud Service Description"].astype(str)

    # Initialize totals
    total_current_cost = 0
    total_prepaid_cost = 0
    total_first_year_cost = 0
    total_updated_annual_cost = 0
    total_subscription_term_fee = 0

    for index, row in df.iterrows():
        # Calculate basic values for all billing terms
        current_monthly_cost = (row['Annual Unit Fee'] / 12) * row['Unit Quantity']
        current_annual_cost = row['Unit Quantity'] * row['Annual Unit Fee']
        new_annual_cost = (row['Unit Quantity'] + row['Additional Licenses']) * row['Annual Unit Fee']

        df.at[index, 'Current Monthly Cost'] = current_monthly_cost
        df.at[index, 'Current Annual Cost'] = current_annual_cost
        df.at[index, 'Updated Annual Cost'] = new_annual_cost

        if billing_term == 'Monthly':
            fractional_month = months_remaining % 1
            first_month_factor = fractional_month if fractional_month > 0 else 1.0
        
            # ✅ Only calculate First Month Co-Termed Cost for additional licenses
            df.at[index, 'First Month Co-Termed Cost'] = conditional_round(
                (row['Additional Licenses'] * row['Annual Unit Fee'] / 12) * first_month_factor
            )
        
            # ✅ Monthly Co-Termed Cost includes both current + new licenses
            df.at[index, 'Monthly Co-Termed Cost'] = conditional_round(
                ((row['Unit Quantity'] + row['Additional Licenses']) * row['Annual Unit Fee']) / 12
            )
        
            # ✅ New Monthly Cost includes both current + new licenses
            df.at[index, 'New Monthly Cost'] = conditional_round(
                ((row['Unit Quantity'] + row['Additional Licenses']) * row['Annual Unit Fee']) / 12
            )
        
            # ✅ Subscription term total (total months)
            df.at[index, 'Subscription Term Total Service Fee'] = conditional_round(
                df.at[index, 'New Monthly Cost'] * total_term
            )
        
        elif billing_term == 'Annual':
            # ✅ First Year Co-Termed Cost ONLY for additional licenses
            df.at[index, 'First Year Co-Termed Cost'] = conditional_round(
                (row['Additional Licenses'] * row['Annual Unit Fee'] * (12 - (months_elapsed % 12))) / 12
            )
        
            # ✅ Subscription Term Total Service Fee based on years remaining
            years_remaining = total_term / 12
            df.at[index, 'Subscription Term Total Service Fee'] = conditional_round(
                new_annual_cost * years_remaining
            )
        
        elif billing_term == 'Prepaid':
            # ✅ Ensure necessary columns exist
            for col in ['Current Prepaid Cost', 'Prepaid Co-Termed Cost', 'Remaining Subscription Total']:
                if col not in df.columns:
                    df[col] = 0.0
        
            # ✅ Calculate Current Prepaid Cost for the **full agreement term**
            current_prepaid_cost = row['Annual Unit Fee'] * row['Unit Quantity']

        
            # ✅ Correct **Prepaid Co-Termed Cost Calculation** (based on remaining months)
            prepaid_co_termed_cost = conditional_round(
                row['Annual Unit Fee'] / agreement_term * months_remaining * row['Additional Licenses']
            )
        
            # ✅ Calculate Remaining Subscription Total = (Current Prepaid Cost + Prepaid Co-Termed Cost)
            remaining_subscription_total = current_prepaid_cost + prepaid_co_termed_cost
        
            # ✅ Store values in DataFrame
            df.at[index, 'Current Prepaid Cost'] = current_prepaid_cost
            df.at[index, 'Prepaid Co-Termed Cost'] = prepaid_co_termed_cost
            df.at[index, 'Remaining Subscription Total'] = remaining_subscription_total













    # Remove any existing total row
    df = df[df["Cloud Service Description"] != "Total Licensing Cost"].copy()

    df["Cloud Service Description"] = df["Cloud Service Description"].astype(str)

    # Create Total Licensing Cost row with conditional columns based on billing term
    total_row_data = {
        "Cloud Service Description": ["Total Licensing Cost"],
        "Unit Quantity": [df["Unit Quantity"].sum()],
        "Additional Licenses": [df["Additional Licenses"].sum()],
        "Annual Unit Fee": [df["Annual Unit Fee"].mean()],  # Use mean for unit fee
    }
    
    # ✅ Add billing term specific columns
    if billing_term == "Prepaid":
        if "Current Prepaid Cost" in df.columns:
            total_row_data["Current Prepaid Cost"] = [df["Current Prepaid Cost"].sum()]
        if "Prepaid Co-Termed Cost" in df.columns:
            total_row_data["Prepaid Co-Termed Cost"] = [df["Prepaid Co-Termed Cost"].sum()]
        if "Remaining Subscription Total" in df.columns:
            total_row_data["Remaining Subscription Total"] = [df["Remaining Subscription Total"].sum()]  # ✅ Fix missing value

    if billing_term == "Annual":
        if "First Year Co-Termed Cost" in df.columns:
            total_row_data["First Year Co-Termed Cost"] = [df["First Year Co-Termed Cost"].sum()]
        if "Current Annual Cost" in df.columns:
            total_row_data["Current Annual Cost"] = [df["Current Annual Cost"].sum()]
        if "Updated Annual Cost" in df.columns:
            total_row_data["Updated Annual Cost"] = [df["Updated Annual Cost"].sum()]
    
    if billing_term == "Monthly":
        if "First Month Co-Termed Cost" in df.columns:
            total_row_data["First Month Co-Termed Cost"] = [df["First Month Co-Termed Cost"].sum()]
        if "Current Monthly Cost" in df.columns:
            total_row_data["Current Monthly Cost"] = [df["Current Monthly Cost"].sum()]
        if "New Monthly Cost" in df.columns:
            total_row_data["New Monthly Cost"] = [df["New Monthly Cost"].sum()]
    
    # Always add the subscription term total
    if "Subscription Term Total Service Fee" in df.columns:
        total_row_data["Subscription Term Total Service Fee"] = [df["Subscription Term Total Service Fee"].sum()]
    
    # Convert dictionary to DataFrame
    total_row = pd.DataFrame(total_row_data)

    # Append the total row back
    df = pd.concat([df, total_row], ignore_index=True)

    # Final Totals for return values
    total_current_cost = df.loc[df['Cloud Service Description'] != 'Total Licensing Cost', 'Current Annual Cost'].sum()
    
    if billing_term == 'Prepaid':
        # For Prepaid, set total_current_cost to the sum of Current Prepaid Cost
        if 'Current Prepaid Cost' in df.columns:
            total_current_cost = df.loc[df['Cloud Service Description'] != 'Total Licensing Cost', 'Current Prepaid Cost'].sum()
        
        if 'Prepaid Co-Termed Cost' in df.columns:
            total_prepaid_cost = df.loc[df['Cloud Service Description'] != 'Total Licensing Cost', 'Prepaid Co-Termed Cost'].sum()
        
        if 'Subscription Term Total Service Fee' in df.columns:
            total_subscription_term_fee = df.loc[df['Cloud Service Description'] != 'Total Licensing Cost', 'Subscription Term Total Service Fee'].sum()
            
    elif billing_term == 'Annual':
        if 'First Year Co-Termed Cost' in df.columns:
            total_first_year_cost = df.loc[df['Cloud Service Description'] != 'Total Licensing Cost', 'First Year Co-Termed Cost'].sum()
        
        if 'Updated Annual Cost' in df.columns:
            total_updated_annual_cost = df.loc[df['Cloud Service Description'] != 'Total Licensing Cost', 'Updated Annual Cost'].sum()
        
        if 'Subscription Term Total Service Fee' in df.columns:
            total_subscription_term_fee = df.loc[df['Cloud Service Description'] != 'Total Licensing Cost', 'Subscription Term Total Service Fee'].sum()
            
    else:  # Monthly
        if 'Subscription Term Total Service Fee' in df.columns:
            total_subscription_term_fee = df.loc[df['Cloud Service Description'] != 'Total Licensing Cost', 'Subscription Term Total Service Fee'].sum()
        
        if 'Updated Annual Cost' in df.columns:
            total_updated_annual_cost = df.loc[df['Cloud Service Description'] != 'Total Licensing Cost', 'Updated Annual Cost'].sum()

    return df, total_current_cost, total_prepaid_cost, total_first_year_cost, total_updated_annual_cost, total_subscription_term_fee



def generate_pdf(billing_term, months_remaining, extension_months, total_current_cost, total_prepaid_cost, 
                total_first_year_cost, total_updated_annual_cost, total_subscription_term_fee, data, agreement_term, 
                logo_path=None):
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

    # ✅ FIX: Ensure column exists before referencing it
    if 'Remaining Subscription Total' in data.columns:
        remaining_total = float(data['Remaining Subscription Total'].sum())
    else:
        remaining_total = 0.0  # Default value if column is missing

    # Print headers
    pdf.set_font("Arial", "B", 7)
    
    # Print headers in a single row using cell method
    pdf.cell(w_desc, 6, 'Cloud Service Description', 1, 0, 'C')
    pdf.cell(w_qty, 6, 'Unit Quantity', 1, 0, 'C')
    pdf.cell(w_fee, 6, 'Annual Unit Fee', 1, 0, 'C')
    pdf.cell(w_lic, 6, 'Additional Licenses', 1, 0, 'C')
    pdf.cell(w_cost, 6, "Cost", 1, 0, 'C')
    pdf.cell(w_total, 6, "Remaining Subscription Total", 1, 1, 'C')
    
    # Add a small line break
    pdf.ln(1)

    # ✅ FIX: Ensure we process rows correctly
    pdf.set_font("Arial", "", 7)
    for _, row in data.iterrows():
        pdf.cell(w_desc, 6, str(row.get('Cloud Service Description', 'N/A')), 1, 0, 'L')
        pdf.cell(w_qty, 6, str(row.get('Unit Quantity', 0)), 1, 0, 'C')
        pdf.cell(w_fee, 6, f"${float(row.get('Annual Unit Fee', 0)):.2f}", 1, 0, 'R')
        pdf.cell(w_lic, 6, str(row.get('Additional Licenses', 0)), 1, 0, 'C')
        
        # Dynamically select the appropriate cost column
        if billing_term == 'Monthly':
            cost_value = row.get('First Month Co-Termed Cost', 0)
        elif billing_term == 'Annual':
            cost_value = row.get('First Year Co-Termed Cost', 0)
        else:  # Prepaid
            cost_value = row.get('Prepaid Co-Termed Cost', 0)
        
        pdf.cell(w_cost, 6, f"${float(cost_value):,.2f}", 1, 0, 'R')
        pdf.cell(w_total, 6, f"${remaining_total:,.2f}", 1, 1, 'R')  # ✅ Use calculated value
        
        pdf.set_font("Arial", "", 7)

    # Licensing Summary
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Licensing Summary", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, "Total Current Licenses: {}".format(total_current_cost), ln=True)
    pdf.cell(0, 6, "Total Additional Licenses: {}".format(total_updated_annual_cost), ln=True)
    pdf.ln(8)
    
    # Current vs New Cost Summary
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Current vs New Cost Summary", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, "Current Annual Cost: ${:,.2f}".format(total_current_cost), ln=True)
    pdf.cell(0, 6, "Updated Annual Cost: ${:,.2f}".format(total_updated_annual_cost), ln=True)
    pdf.cell(0, 6, "Total Subscription Term Cost: ${:,.2f}".format(total_subscription_term_fee), ln=True)
    pdf.ln(8)
    
    # Cost Comparison Chart Placeholder
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Cost Comparison Chart", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, "(Chart to be generated separately in the app UI)", ln=True)
    pdf.ln(10)
    
    # ✅ FIX: Move return statement to the end
    pdf_buffer = io.BytesIO()
    pdf_data = pdf.output(dest='S').encode('latin1')  # Get as string and encode
    pdf_buffer.write(pdf_data)
    pdf_buffer.seek(0)
        
    return pdf_buffer
def generate_email_template(billing_term, df, current_cost, first_cost, total_subscription_cost, updated_annual_cost=0, total_first_year_co_termed_cost=0, agreement_term=0, months_remaining=0):
    license_list = []
    
    # Ensure df is a valid Pandas DataFrame
    if not isinstance(df, pd.DataFrame):
        raise ValueError("generate_email_template(): 'df' is not a valid Pandas DataFrame")

    # Extract correct co-term cost and actual license names from df
    for index, row in df.iterrows():
        license_name = row.get("Cloud Service Description", f"License {index + 1}")  # Get actual license name
        first_year_co_termed = row.get("First Year Co-Termed Cost", 0)
        first_month_co_termed = row.get("First Month Co-Termed Cost", 0)
        new_monthly_cost = row.get("New Monthly Cost", 0)
        current_prepaid_cost = row.get("Current Prepaid Cost", 0)
        prepaid_co_termed_cost = row.get("Prepaid Co-Termed Cost", 0)

        license_entry = {
            "name": license_name,
            "first_year_co_termed": first_year_co_termed,
            "first_month_co_termed": first_month_co_termed,
            "new_monthly_cost": new_monthly_cost,
            "current_prepaid_cost": current_prepaid_cost,
            "prepaid_co_termed_cost": prepaid_co_termed_cost
        }

        license_list.append(license_entry)

    # ✅ Rename the last license to "Total"
    if license_list:
        license_list[-1]["name"] = "Total"

    # ✅ Generate the License Cost Breakdown for Prepaid Billing
    prepaid_license_cost_breakdown = '\n'.join([
        f"- {license['name']} - Current Prepaid Cost: ${license['current_prepaid_cost']:,.2f}, "
        f"Additional Licenses Cost: ${license['prepaid_co_termed_cost']:,.2f}"
        for license in license_list if license['name'] != 'Total'
    ])

    # ✅ Generate the License Cost Breakdown for Annual Billing
    annual_license_cost_breakdown = ""
    if billing_term == "Annual":
        annual_license_cost_breakdown = '\n'.join([
            f"- {license['name']} - First Year Co-Termed Cost: ${license['first_year_co_termed']:,.2f}"
            for license in license_list
        ])

    # ✅ Generate the License Cost Breakdown for Monthly Billing
    monthly_license_cost_breakdown = ""
    if billing_term == "Monthly":
        monthly_license_cost_breakdown = '\n'.join([
            f"- {license['name']} - First Month Co-Termed Cost: ${license['first_month_co_termed']:,.2f}, New Monthly Cost: ${license['new_monthly_cost']:,.2f}"
            for license in license_list
        ])

    # ✅ Update the email template
    email_templates = {
        
        'Monthly': f"""Dear Customer,

We are writing to inform you about the updated co-terming cost for your monthly billing arrangement.

Current Agreement:
- Current Monthly Cost: ${current_cost/12:,.2f}

### License Cost Breakdown:
{monthly_license_cost_breakdown}

Updated Cost Summary:
- First Month Co-Termed Cost: ${first_cost:,.2f}
- New Monthly Cost: ${updated_annual_cost/12:,.2f}
- Total Remaining Subscription Cost: ${total_subscription_cost:,.2f}

Key Details:
- The first month's co-termed cost reflects your current service adjustments.
- Your total subscription cost covers the entire term of the agreement.

Next Steps:
1. Please carefully review the cost breakdown above.
2. If you approve these terms, kindly reply to this email with your confirmation.
3. If you have any questions or concerns, please contact our sales team.

We appreciate your continued business and look forward to your approval.

Best regards,
Your Signature""",

        'Annual': f"""Dear Customer,

We are writing to inform you about the updated co-terming cost for your annual billing arrangement.

### Current Agreement:
- **Current Annual Cost:** ${current_cost:,.2f}

### License Cost Breakdown:
{annual_license_cost_breakdown}

### Updated Cost Summary:
- **Total First Year Co-Termed Cost:** ${total_first_year_co_termed_cost:,.2f}
- **Updated Annual Cost:** ${updated_annual_cost:,.2f}
- **Total Remaining Subscription Cost:** ${total_subscription_cost:,.2f}

### Key Details:
- The first year's co-termed cost reflects your current service adjustments.
- Your total subscription cost covers the entire term of the agreement.

### Next Steps:
1. Please carefully review the cost breakdown above.
2. If you approve these terms, kindly reply to this email with your confirmation.
3. If you have any questions or concerns, please contact our sales team.

We appreciate your continued business and look forward to your approval.

Best regards,  
Your Signature""",
    
        'Prepaid': f"""Dear Customer,

We are writing to inform you about the updated co-terming cost for your prepaid billing arrangement.

### Current Agreement:
- **Original Agreement Term:** {agreement_term} months
- **Remaining Months:** {months_remaining:.2f} months
- **Current Prepaid Cost (Remaining Months):** ${current_cost:,.2f}

### Prepaid License Cost Breakdown:
{prepaid_license_cost_breakdown}

### Updated Cost Summary:
- **Additional Licenses Prepaid Cost:** ${first_cost:,.2f}
- **Total Subscription Cost (All Licenses, Remaining Months):** ${total_subscription_cost:,.2f}

### Key Details:
- The prepaid costs shown are for the remaining {months_remaining:.2f} months of your service term.
- Your total subscription cost covers all licenses for the remaining term.

### Next Steps:
1. Please carefully review the cost breakdown above.
2. If you approve these terms, kindly reply to this email with your confirmation.
3. If you have any questions or concerns, please contact our sales team.

We appreciate your continued business and look forward to your approval.

Best regards,
Your Signature"""
    }
    
    # Return the appropriate template based on billing term
    return email_templates.get(billing_term, "Invalid billing term")


def copy_to_clipboard_button(text, button_text="Copy to Clipboard"):
    # Unique button ID to prevent conflicts
    button_id = f"copy_button_{hash(text)}"

    # JavaScript function to copy text to clipboard
    js_code = f"""
    <script>
    function copyToClipboard_{button_id}() {{
        navigator.clipboard.writeText(`{text.replace("`", "\\`")}`).then(() => {{
            const btn = document.getElementById('{button_id}');
            const originalText = btn.innerHTML;
            btn.innerHTML = 'Copied!';
            setTimeout(() => {{
                btn.innerHTML = originalText;
            }}, 2000);
        }}).catch(err => {{
            console.error('Error copying text:', err);
        }});
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

# Sidebar for navigation and settings
with st.sidebar:
    st.image("logo.png", width=150)
    st.title("Navigation")
    
    # Navigation menu
    nav_options = ["Calculator", "Help & Documentation", "About"]
    nav_selection = st.radio("Go to:", nav_options)
    
    # Set the active tab based on navigation selection
    st.session_state.active_tab = nav_selection.lower().replace(" & ", "_").replace(" ", "_")
    
    st.markdown("---")
    
    # App info
    st.markdown("##### Co-Terming Calculator v1.1")
    st.markdown("© 2025 | CDW")

def update_license_cost():
    """
    Updates the displayed License Cost ($) based on the selected Billing Term.
    """
    for i in range(st.session_state.num_items):  # Loop through all line items
        key = f"fee_{i}"  # Unique key for each license input
        annual_cost = st.session_state.get(key, 0.00)  # Get the entered cost
        
        if st.session_state.billing_term == "Monthly":
            st.session_state[key] = annual_cost / 12  # Convert to monthly cost
        elif st.session_state.billing_term == "Prepaid":
            if st.session_state.months_remaining > 0:
                st.session_state[key] = (annual_cost / st.session_state.months_remaining) * st.session_state.agreement_term
            else:
                st.session_state[key] = annual_cost  # Fallback if months_remaining is zero
                
# Main content area# Main content area
if st.session_state.active_tab == 'calculator':
    # Custom HTML header
    st.markdown('<div class="main-header">Co-Terming Cost Calculator</div>', unsafe_allow_html=True)
    
    # Create tabs without the Customer Info tab
    tabs = st.tabs(["Agreement Info", "Licensing", "Results", "Email Template"])
    
    with tabs[0]:
        st.markdown('<div class="sub-header">Agreement Information</div>', unsafe_allow_html=True)
        
        # Add a separator
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # Agreement info section
        left_col, right_col = st.columns(2)
        
        with left_col:
            # Agreement start date with consistent styling
            st.markdown('<p class="field-label">Agreement Start Date:</p>', unsafe_allow_html=True)
            default_start_date = datetime.today() - pd.DateOffset(months=6)
            agreement_start_date = st.date_input(
                "",  # Empty label since we're using custom styling
                value=default_start_date,
                max_value=datetime.today(),
                key="agreement_start_date",
                label_visibility="collapsed"
            )

            # ✅ Co-Terming Start Date Selection
            st.markdown('<p class="field-label">Co-Termed Start Date:</p>', unsafe_allow_html=True)
            
            # Default Co-Termed Start Date (set to today or future)
            default_co_termed_start_date = datetime.today()
            
            # ✅ Allow user to manually select a future co-termed start date
            co_termed_start_date = st.date_input(
                "Select Co-Termed Start Date:",
                value=default_co_termed_start_date,
                min_value=datetime.today(),  # ✅ Ensure co-termed start date is in the future
                max_value=datetime.today() + pd.DateOffset(years=5),  # Optional: Limit selection
                key="co_termed_start_date"
            )
            
            st.markdown(f"**Selected Co-Termed Start Date:** {co_termed_start_date.strftime('%Y-%m-%d')}")


        with right_col:
            # Agreement term with consistent styling
            st.markdown('<p class="field-label">Agreement Term (Months):</p>', unsafe_allow_html=True)
            agreement_term = st.number_input(
                "",
                min_value=1, 
                value=36, 
                step=1, 
                format="%d",
                key="agreement_term",
                label_visibility="collapsed"
            )
        
            # ✅ Convert dates to pandas timestamps
            co_termed_start_datetime = pd.Timestamp(co_termed_start_date)
            agreement_start_datetime = pd.Timestamp(agreement_start_date)
        
            # ✅ Calculate co-termed months remaining
            co_termed_months_remaining = calculate_co_termed_months_remaining(
                co_termed_start_datetime, agreement_start_datetime, agreement_term
            )
        
            # ✅ Display the correct months remaining
            st.markdown(f"**Calculated Months Remaining:** {co_termed_months_remaining:.2f}")
        
            # ✅ Place the checkbox BEFORE using `use_calculated_months`
            use_calculated_months = st.checkbox(
                "Use calculated months remaining", 
                value=True,
                key="use_calculated_months_checkbox"  # ✅ Unique key to prevent duplication
            )
        
            # ✅ Use calculated months if checked, otherwise allow manual input
            if use_calculated_months:
                months_remaining = co_termed_months_remaining  # ✅ Use correct variable name
                st.markdown(f"""
                <div class="info-display">
                    <span class="info-label">Calculated Months Remaining:</span> {months_remaining:.2f}
                </div>
                """, unsafe_allow_html=True)
            else:
                months_remaining = st.number_input(
                    "", 
                    min_value=0.01, 
                    max_value=float(agreement_term), 
                    value=co_termed_months_remaining,  # ✅ Use the correct variable name
                    step=0.01, 
                    format="%.2f",
                    key="manual_months_input",  # ✅ Unique key
                    label_visibility="collapsed"
                )



        
        # Add a separator with consistent styling
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # Extension option with better styling
        extension_col1, extension_col2 = st.columns([1, 3])
        
        with extension_col1:
            add_extension = st.checkbox("Add Agreement Extension?", key="add_extension")
        
        if add_extension:
            with extension_col2:
                st.markdown('<p class="field-label">Extension Period (Months):</p>', unsafe_allow_html=True)
                extension_months = st.number_input(
                    "", 
                    min_value=1, 
                    value=12, 
                    step=1, 
                    format="%d",
                    key="extension_months",
                    label_visibility="collapsed"
                )
                total_term = months_remaining + extension_months
                
                # Display total term with consistent styling
                st.markdown(f"""
                <div class="total-display">
                    <span class="info-label">Total Term:</span> {total_term:.2f} months
                </div>
                """, unsafe_allow_html=True)
        else:
            extension_months = 0
            total_term = months_remaining
            


with tabs[1]: 
    st.markdown('<div class="sub-header">Service Information</div>', unsafe_allow_html=True)

    # ✅ Create two columns for instructions
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### 📢 Important Instructions:
        - **Enter the number of line items** based on the licenses you need to co-term.
        - **Billing Term must be selected** to calculate costs properly.
        - **Unit Quantity**: The number of licenses currently in use.
        - **Additional Licenses**: New licenses being added (leave as 0 if no new licenses).
        - ⚠️ **Make sure all fields are correctly filled before calculating costs.**
        """)

    with col2:
        st.markdown("""
        ### For Monthly Agreements:
        - **Enter the Monthly license cost in the "License Cost ($) field.
    
        ### For Annual Agreements:
        - **Enter the Annual license cost in the "License Cost ($) field.
    
        ### For Pre-Paid Agreements:
        - **Enter the FULL Pre-Paid cost for each license.  (Vision calculates the remaining term for the cost of the license in the BOM.  You will need to find the full pre-paid cost for each license and add that to the calculator below)
        
        """)

        # Add a separator for better layout
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Initialize the dataframe to store licensing data
    columns = ["Cloud Service Description", "Unit Quantity", "Annual Unit Fee", "Additional Licenses"]
    data = pd.DataFrame(columns=columns)  # ✅ Fix: Initialize an empty DataFrame

    # Number of items
    st.session_state.num_items = st.number_input("Number of Line Items:", min_value=1, value=1, step=1, format="%d")

    billing_term = st.selectbox(
        "Billing Term", ["Annual", "Prepaid", "Monthly"], key="billing_term_licensing"
    )

    # Create a container for the line items
    line_items_container = st.container()

    with line_items_container:
        for i in range(st.session_state.num_items):
            st.markdown(f"**Item {i+1}**")
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

            # Unique keys for each input
            service_key = f"service_{i}"
            qty_key = f"qty_{i}"
            fee_key = f"fee_{i}"
            add_lic_key = f"add_lic_{i}"

            # Input fields
            service = col1.text_input("Service Description", key=service_key, placeholder="Enter service name")
            qty = col2.number_input("Quantity", min_value=0, value=1, step=1, format="%d", key=qty_key)
            
            # License Cost ($) field that updates dynamically
            fee = col3.number_input(
                "License Cost ($)", 
                min_value=0.0, 
                value=st.session_state.get(fee_key, 0.00), 
                step=10.0, 
                format="%.2f", 
                key=fee_key
            )

            add_lic = col4.number_input("Add. Licenses", min_value=0, value=0, step=1, format="%d", key=add_lic_key)
            
            # Store the row data
            row_data = {
                "Cloud Service Description": service,
                "Unit Quantity": qty,
                "Annual Unit Fee": fee,
                "Additional Licenses": add_lic,
            }
            
            # ✅ Fix: Append new row to the dataframe
            new_row = pd.DataFrame([row_data])
            data = pd.concat([data, new_row], ignore_index=True)  # ✅ No more NameError
        
            
with tabs[2]:
    st.markdown('<div class="sub-header">Results</div>', unsafe_allow_html=True)

    # ✅ Fix: Check for empty service descriptions
    empty_services = data["Cloud Service Description"].isnull() | (data["Cloud Service Description"] == "")

    # Check if we have valid data before calculating
    valid_data = not empty_services.any() and len(data) > 0
    
    # Create a fixed layout for the Results page
    button_container = st.container()  # ✅ This keeps the button static
    results_placeholder = st.container()  # ✅ This holds the dynamic results
    
    # Place the button inside the static container
    with button_container:
        st.markdown("### Run Cost Calculation")  # ✅ Add a section title for clarity
        calculate_button = st.button("Calculate Costs", disabled=not valid_data, 
                                     help="Enter all required information to enable calculations")
    
    # Process calculations inside the results placeholder
    with results_placeholder:
        if calculate_button and valid_data:
            with st.spinner("Calculating costs..."):
                processed_data, total_current_cost, total_prepaid_cost, total_first_year_cost, total_updated_annual_cost, total_subscription_term_fee = calculate_costs(
                    data,
                    agreement_term,
                    months_remaining,
                    extension_months,
                    billing_term
                )
        
                # ✅ Store the calculated values in session state
                st.session_state.calculation_results = {
                    "processed_data": processed_data,
                    "total_current_cost": total_current_cost,
                    "total_prepaid_cost": total_prepaid_cost,
                    "total_first_year_cost": total_first_year_cost,
                    "total_updated_annual_cost": total_updated_annual_cost,
                    "total_subscription_term_fee": total_subscription_term_fee
                }

    
    
            
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

        # ✅ Ensure session state variable is initialized before access
    if "calculation_results" not in st.session_state:
        st.session_state.calculation_results = None  # ✅ Initializes it safely

    if st.session_state.calculation_results is not None:  # ✅ Prevents KeyError
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
                        "Monthly Co-Termed Cost", "First Month Co-Termed Cost", "Current Annual Cost"]:
             if col in displayed_data.columns:
                displayed_data[col] = pd.to_numeric(displayed_data[col], errors='coerce')

                           
             # After creating displayed_data and before displaying it with st.dataframe()
            if 'Current Annual Cost' in displayed_data.columns and 'First Year Co-Termed Cost' in displayed_data.columns:
                # Get all column names
                cols = displayed_data.columns.tolist()
                
                # Remove 'Current Annual Cost' from its current position
                if 'Current Annual Cost' in cols:
                    cols.remove('Current Annual Cost')
                
                # Find the position of 'First Year Co-Termed Cost'
                if 'First Year Co-Termed Cost' in cols:
                    updated_pos = cols.index('First Year Co-Termed Cost')
                    # Insert 'Current Annual Cost' right after 'First Year Co-Termed Cost'
                    cols.insert(updated_pos + 1, 'Current Annual Cost')
                    
                    # Reorder the DataFrame
                    displayed_data = displayed_data[cols]

            # Adjust column order for Monthly billing (Ensure "Cloud Service Description" is included)
            if billing_term == 'Monthly':
                column_order = [
                    "Cloud Service Description",  # ✅ Ensure this stays in the output
                    "Unit Quantity", "Annual Unit Fee", "Additional Licenses", 
                    "First Month Co-Termed Cost", "Current Monthly Cost", 
                    "New Monthly Cost", "Subscription Term Total Service Fee"
                ]
            
                # Keep only columns that exist in the DataFrame to avoid errors
                displayed_data = displayed_data[[col for col in column_order if col in displayed_data.columns]]
                
            elif billing_term == 'Annual':  # ✅ Add missing Annual column order
                column_order = [
                    "Cloud Service Description",
                    "Unit Quantity", "Annual Unit Fee", "Additional Licenses",
                    "First Year Co-Termed Cost",
                    "Current Annual Cost",  # ✅ Move Current Annual Cost before Updated Annual Cost
                    "Updated Annual Cost",  # ✅ Move Updated Annual Cost after Current Annual Cost
                    "Subscription Term Total Service Fee"
                ]
                displayed_data = displayed_data[[col for col in column_order if col in displayed_data.columns]]

            elif billing_term == 'Prepaid':
                column_order = [
                    "Cloud Service Description",
                    "Unit Quantity",
                    "Additional Licenses",
                    "Current Prepaid Cost",
                    "Prepaid Co-Termed Cost",
                    "Remaining Subscription Total"
                ]
            
                # Keep only columns that exist in the DataFrame to avoid errors
                displayed_data = displayed_data[[col for col in column_order if col in displayed_data.columns]]


                
            # ✅ Ensure only existing columns are formatted
            columns_to_format = {
                "Annual Unit Fee": "${:,.2f}",
                "Remaining Subscription Total": "${:,.2f}"
            }
            
            # ✅ Conditionally add columns based on the billing term
            if billing_term == "Prepaid":
                columns_to_format["Current Prepaid Cost"] = "${:,.2f}"
                columns_to_format["Prepaid Co-Termed Cost"] = "${:,.2f}"

            
            if billing_term == "Annual":
                columns_to_format["First Year Co-Termed Cost"] = "${:,.2f}"
                columns_to_format["Updated Annual Cost"] = "${:,.2f}"
                columns_to_format["Current Annual Cost"] = "${:,.2f}"

            
            if billing_term == "Monthly":
                columns_to_format["First Month Co-Termed Cost"] = "${:,.2f}"
                columns_to_format["Current Monthly Cost"] = "${:,.2f}"
                columns_to_format["New Monthly Cost"] = "${:,.2f}"

            
            # Rename the column before displaying
            displayed_data = displayed_data.rename(columns={"Subscription Term Total Service Fee": "Remaining Subscription Total"})
            
            # Format and display the DataFrame
            st.dataframe(displayed_data.style.format(columns_to_format).set_properties(**{"white-space": "normal"}))


           
                    
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
            # Convert columns to numeric values to avoid errors when summing
            processed_data["Unit Quantity"] = pd.to_numeric(processed_data["Unit Quantity"], errors="coerce").fillna(0)
            processed_data["Additional Licenses"] = pd.to_numeric(processed_data["Additional Licenses"], errors="coerce").fillna(0)
            
            # Now safely calculate the total licenses
            total_current_licenses = processed_data.loc[
                processed_data["Cloud Service Description"] != "Total Licensing Cost", "Unit Quantity"
            ].sum()
            
            total_additional_licenses = processed_data.loc[
                processed_data["Cloud Service Description"] != "Total Licensing Cost", "Additional Licenses"
            ].sum()
            
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
                # ✅ Define Original and Extended Agreement Terms
                original_term_years = agreement_term / 12  # ✅ Convert original agreement term to years
                total_term_years = (months_remaining + extension_months) / 12  # ✅ Convert total agreement term (including extensions) to years
        
            if billing_term == "Monthly":
                current_cost = total_current_cost / 12
                new_cost = total_updated_annual_cost / 12
                cost_label = "Monthly Cost"
        
                # ✅ Current TCO (Original Agreement Term) & New TCO (Extended Term)
                current_tco = current_cost * (agreement_term)  # ✅ Only original term in months
                new_tco = new_cost * (months_remaining + extension_months)  # ✅ Extended term
        
            elif billing_term == "Annual":
                current_cost = total_current_cost
                new_cost = total_updated_annual_cost
                cost_label = "Annual Cost"
        
                # ✅ Current TCO (Original Agreement Term) & New TCO (Extended Term)
                current_tco = new_cost * total_term_years 
                new_tco = current_cost * original_term_years
        
            if billing_term == "Prepaid":
                current_cost = total_current_cost
                new_cost = total_current_cost + total_prepaid_cost  # ✅ Fix for Prepaid
                cost_label = "Prepaid Cost"
            
                # ✅ Create a comparison table WITHOUT Total Cost of Ownership for Prepaid
                comparison_data = {
                    "Cost Type": [
                        f"Current {cost_label}",
                        f"New {cost_label}",
                        "Difference",
                        "Percentage Change"
                    ],
                    "Amount": [
                        f"${current_cost:,.2f}",
                        f"${new_cost:,.2f}",
                        f"${new_cost - current_cost:,.2f}",
                        f"{((new_cost - current_cost) / current_cost * 100) if current_cost > 0 else 0:,.2f}%"
                    ]
                }
            
                # ✅ Prevent NameError: Skip TCO calculations for Prepaid
                current_tco = None
                new_tco = None  # ✅ Prevents NameError later
            
            else:  # ✅ Annual & Monthly Billing Terms
                current_cost = total_current_cost
                new_cost = total_updated_annual_cost
                cost_label = "Annual Cost" if billing_term == "Annual" else "Monthly Cost"
            
                # ✅ Define Total Cost of Ownership (TCO)
                original_term_years = agreement_term / 12
                total_term_years = (months_remaining + extension_months) / 12
            
                current_tco = current_cost * original_term_years
                new_tco = new_cost * total_term_years
            
                # ✅ Create a comparison table INCLUDING Total Cost of Ownership
                comparison_data = {
                    "Cost Type": [
                        f"Current {cost_label}",
                        f"New {cost_label}",
                        "Difference",
                        "Percentage Change",
                        f"New Total Cost of Ownership ({cost_label})",
                        f"Current Total Cost of Ownership ({cost_label})"
                    ],
                    "Amount": [
                        f"${current_cost:,.2f}",
                        f"${new_cost:,.2f}",
                        f"${new_cost - current_cost:,.2f}",
                        f"{((new_cost - current_cost) / current_cost * 100) if current_cost > 0 else 0:,.2f}%",
                        f"${current_tco:,.2f}",
                        f"${new_tco:,.2f}"
                    ]
                }
            
            # ✅ Check before using `new_tco` and `current_tco`
            if new_tco is not None and current_tco is not None:
                if new_tco > current_tco:
                    change_pct = ((new_tco - current_tco) / current_tco * 100) if current_tco > 0 else 0
                    st.info(f"The new {billing_term.lower()} cost represents a {change_pct:.1f}% increase from the current total cost of ownership.")
                elif new_tco < current_tco:
                    change_pct = ((current_tco - new_tco) / current_tco * 100) if current_tco > 0 else 0
                    st.success(f"The new {billing_term.lower()} cost represents a {change_pct:.1f}% decrease from the current total cost of ownership.")
                else:
                    st.info(f"The new {billing_term.lower()} cost is identical to the current total cost of ownership.")
            
            # ✅ Only display table if defined
            st.table(pd.DataFrame(comparison_data))

                      
            st.markdown("### Cost Comparison")
            
            # Prepare chart data based on billing term
            if billing_term == 'Monthly':
                # Get values from the Total Services Cost row
                total_row = processed_data[processed_data['Cloud Service Description'] == 'Total Licensing Cost']
                
                # Make sure these columns exist in the dataframe
                monthly_co_termed = float(total_row['Monthly Co-Termed Cost'].iloc[0]) if 'Monthly Co-Termed Cost' in total_row.columns else 0.0
                # ✅ Ensure First Month Co-Termed Cost pulls the correct sum
                first_month_co_termed = float(total_row["First Month Co-Termed Cost"].sum()) if "First Month Co-Termed Cost" in total_row.columns else 0.0
                
                # Current monthly cost
                current_monthly = total_current_cost / 12
                new_monthly = (total_updated_annual_cost / 12) if total_updated_annual_cost > 0 else 0
                
                chart_data = {
                    "currentCost": float(total_current_cost / 12),  # ✅ Current Monthly Cost
                    "coTermedMonthly": float(first_month_co_termed),  # ✅ Now correctly included in chart
                    "newMonthly": float(total_updated_annual_cost / 12),  # ✅ Corrected "New Monthly Cost"
                    "subscription": float(total_subscription_term_fee)
                }

            elif billing_term == 'Annual':
                chart_data = {
                    "currentCost": float(total_current_cost),
                    "firstYearCoTerm": float(total_first_year_cost),
                    "newAnnual": float(total_updated_annual_cost),
                    "subscription": float(total_subscription_term_fee)
                }
            # For the Prepaid billing term
            elif billing_term == 'Prepaid':
                # Get the values from the Total Licensing Cost row
                total_row = processed_data[processed_data['Cloud Service Description'] == 'Total Licensing Cost']
                
                # Get the current prepaid cost (remaining months)
                current_prepaid_cost = float(total_row['Current Prepaid Cost'].iloc[0]) if 'Current Prepaid Cost' in total_row.columns else 0.0
                
                # Get the additional licenses prepaid cost
                additional_prepaid = float(total_row['Prepaid Co-Termed Cost'].iloc[0]) if 'Prepaid Co-Termed Cost' in total_row.columns else 0.0
                
                # Total subscription cost
                subscription_total = float(total_row['Subscription Term Total Service Fee'].iloc[0]) if 'Subscription Term Total Service Fee' in total_row.columns else 0.0
                
                # Create chart data for prepaid view
                chart_data = {
                    "currentCost": current_prepaid_cost,  # Current prepaid cost for remaining months
                    "coTermedPrepaid": additional_prepaid,  # Additional licenses prepaid cost
                    "subscription": subscription_total  # Total subscription cost
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
            )
                
            # In the Results tab, update the download button
            st.download_button(
                label="Download PDF Report",
                data=pdf_buffer,
                file_name="coterming_report.pdf",
                mime="application/pdf",
                key="pdf_download"
            )
with tabs[3]:
    st.markdown('<div class="sub-header">Email Template</div>', unsafe_allow_html=True)

    # Check if we have calculation results
    if st.session_state.calculation_results:
        results = st.session_state.calculation_results
        total_current_cost = results["total_current_cost"]
        total_prepaid_cost = results["total_prepaid_cost"]
        total_first_year_cost = results["total_first_year_cost"]
        total_updated_annual_cost = results["total_updated_annual_cost"]
        total_subscription_term_fee = results["total_subscription_term_fee"]
        total_first_year_co_termed_cost = total_first_year_cost  

        # Determine which cost value to use based on billing term
        if billing_term == 'Monthly':
            first_cost = results["processed_data"][results["processed_data"]['Cloud Service Description'] == 'Total Licensing Cost']['First Month Co-Termed Cost'].iloc[0]
        elif billing_term == 'Annual':
            first_cost = total_first_year_cost
        else:  # Prepaid
            first_cost = total_prepaid_cost

        # Generate email template
        email_content = generate_email_template(
            billing_term,
            processed_data,
            total_current_cost,
            first_cost,
            total_subscription_term_fee,
            total_updated_annual_cost,
            total_first_year_co_termed_cost
        )

        # Display the email template
        st.markdown("### Email Template Preview")
        st.text_area("Copy Email Content:", email_content, height=800)  # Allows manual copying

        # **📩 Suggested Subject Line**
        st.markdown("### Suggested Email Subject")
        email_subject = f"Co-Terming Cost Proposal - Customer Name"
        st.text_input("Subject Line:", value=email_subject, key="email_subject")

    else:
        st.info("Please calculate costs first to generate an email template.")

# ✅ Move 'elif' outside the previous 'with' block
if st.session_state.active_tab == 'help_documentation':
    st.markdown('<div class="main-header">Help & Documentation</div>', unsafe_allow_html=True)

    # Create an accordion for different help topics
    with st.expander("How to Use This Calculator", expanded=True):
        st.markdown("""
        ### Basic Usage
        
        1. **Agreement Information**: Enter the basic details of the agreement, including billing term, agreement duration, and months remaining.
        
        2. **Service Information**: Add the services that are part of the agreement, including quantities and fees.
        
        3. **Calculate Costs**: Click the 'Calculate Costs' button to generate the results.
        
        4. **Generate Reports**: After calculation, you can download a PDF report or use the generated email template.
        """)
    
    with st.expander("Understanding Billing Terms"):
        st.markdown("""
        ### Billing Terms Explained
        
        - **Annual**: Billing occurs once per year. The calculator shows the first year co-termed cost and the updated annual cost.
        
        - **Monthly**: Billing occurs monthly. The calculator shows the first month co-termed cost and the monthly recurring cost.
        
        - **Prepaid**: The entire subscription period is paid upfront. The calculator shows the total prepaid cost.
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
    
    ### Version History
    
    - **v1.1** (Current): Added customer information, email templates, and theme options
    - **v1.0**: Initial release with basic calculation features
    
    ### Contact
    
    For support or feature requests, please contact your application administrator.
    """)

    # Footer with a credit note
    st.markdown("""
    <div class="footer">
    © 2025 CDW. All rights reserved.
    </div>
    """, unsafe_allow_html=True)

# Add a footer to the main application
st.markdown("""
<div class="footer">
Co-Terming Cost Calculator v1.1 | Developed by Jim Hanus 
</div>
""", unsafe_allow_html=True)
