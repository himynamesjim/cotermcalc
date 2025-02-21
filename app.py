import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF

def calculate_costs(df, agreement_term, months_remaining, billing_term):
    months_elapsed = agreement_term - months_remaining
    total_annual_cost = 0
    total_prepaid_cost = 0
    total_first_year_cost = 0
    total_updated_annual_cost = 0
    total_subscription_term_fee = 0
    
    for index, row in df.iterrows():
        first_month_co_termed_cost = (row['Annual Unit Fee'] / 12) * row['Additional Licenses'] * (months_remaining % 1) if billing_term == 'Monthly' else 0
        monthly_co_termed_cost = (row['Annual Unit Fee'] / 12) * row['Additional Licenses'] if billing_term == 'Monthly' else 0
        annual_total_fee = row['Unit Quantity'] * row['Annual Unit Fee']
        subscription_term_total_fee = ((annual_total_fee * months_remaining) / 12) + ((row['Additional Licenses'] * row['Annual Unit Fee'] * months_remaining) / 12)
        co_termed_prepaid_cost = (row['Additional Licenses'] * row['Annual Unit Fee'] * months_remaining) / 12 if billing_term == 'Prepaid' else 0
        co_termed_prepaid_additional_cost = (row['Additional Licenses'] * row['Annual Unit Fee'] * months_remaining) / 12 if billing_term == 'Prepaid' else 0
        co_termed_first_year_cost = (row['Additional Licenses'] * row['Annual Unit Fee'] * (12 - (months_elapsed % 12))) / 12 if billing_term == 'Annual' else 0
        updated_annual_cost = annual_total_fee + (row['Additional Licenses'] * row['Annual Unit Fee']) if billing_term == 'Annual' else 0
        
        df.at[index, 'Prepaid Co-Termed Cost'] = co_termed_prepaid_cost
        df.at[index, 'Prepaid Additional Licenses Co-Termed Cost'] = co_termed_prepaid_additional_cost
        df.at[index, 'First Year Co-Termed Cost'] = co_termed_first_year_cost
        df.at[index, 'Updated Annual Cost'] = updated_annual_cost
        df.at[index, 'Subscription Term Total Service Fee'] = subscription_term_total_fee
        
        df.at[index, 'First Month Co-Termed Cost'] = first_month_co_termed_cost
        df.at[index, 'Monthly Co-Termed Cost'] = monthly_co_termed_cost
        
        total_annual_cost += updated_annual_cost
        total_prepaid_cost += co_termed_prepaid_cost
        total_first_year_cost += co_termed_first_year_cost
        total_subscription_term_fee += subscription_term_total_fee
    
    total_row = pd.DataFrame({
        "Cloud Service Description": ["Total Services Cost"],
        "Unit Quantity": [df["Unit Quantity"].sum()],
        "Annual Unit Fee": [f"${df['Annual Unit Fee'].sum():,.2f}"],
        "Additional Licenses": [df["Additional Licenses"].sum()],
        "Prepaid Co-Termed Cost": [f"${total_prepaid_cost:,.2f}"],
        "Prepaid Additional Licenses Co-Termed Cost": [f"${df['Prepaid Additional Licenses Co-Termed Cost'].sum():,.2f}"],
        "First Year Co-Termed Cost": [f"${total_first_year_cost:,.2f}"],
        "Updated Annual Cost": [f"${total_updated_annual_cost:,.2f}"],
        "Subscription Term Total Service Fee": [f"${total_subscription_term_fee:,.2f}"],
        "Monthly Co-Termed Cost": [f"${df['Monthly Co-Termed Cost'].sum():,.2f}"],
        "First Month Co-Termed Cost": [f"${df['First Month Co-Termed Cost'].sum():,.2f}"]
    })
    df = pd.concat([df, total_row], ignore_index=True)
    
    return df, total_prepaid_cost, total_first_year_cost, total_updated_annual_cost, total_subscription_term_fee

st.subheader("Results")
if st.button("Calculate Costs"):
    data, total_prepaid_cost, total_first_year_cost, total_updated_annual_cost, total_subscription_term_fee = calculate_costs(data, agreement_term, months_remaining, billing_term)
    st.subheader("Detailed Line Items")
    if billing_term == 'Monthly':
        data = data.drop(columns=['Prepaid Co-Termed Cost', 'First Year Co-Termed Cost', 'Updated Annual Cost'])
    elif billing_term == 'Annual':
        data = data.drop(columns=['Prepaid Co-Termed Cost', 'Monthly Co-Termed Cost', 'First Month Co-Termed Cost'])
    elif billing_term == 'Prepaid':
        data = data.drop(columns=['Monthly Co-Termed Cost', 'First Month Co-Termed Cost', 'First Year Co-Termed Cost', 'Updated Annual Cost'])
    
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
