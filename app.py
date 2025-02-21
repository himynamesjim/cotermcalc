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
        co_termed_prepaid_cost = (row['Additional Licenses'] * row['Annual Unit Fee'] * months_remaining) / agreement_term if billing_term == 'Prepaid' else 0
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
    
    numeric_cols = [
        "Annual Unit Fee", "Prepaid Co-Termed Cost", "Prepaid Additional Licenses Co-Termed Cost",
        "First Year Co-Termed Cost", "Updated Annual Cost", "Subscription Term Total Service Fee",
        "Monthly Co-Termed Cost", "First Month Co-Termed Cost"
    ]
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    total_row = pd.DataFrame({
        "Cloud Service Description": ["Total Services Cost"],
        "Unit Quantity": ["-"],
        "Annual Unit Fee": [f"${df['Annual Unit Fee'].sum():,.2f}"],
        "Additional Licenses": ["-"],
        "Prepaid Co-Termed Cost": [f"${df['Prepaid Co-Termed Cost'].sum():,.2f}"],
        "Prepaid Additional Licenses Co-Termed Cost": [f"${df['Prepaid Additional Licenses Co-Termed Cost'].sum():,.2f}"],
        "First Year Co-Termed Cost": [f"${df['First Year Co-Termed Cost'].sum():,.2f}"],
        "Updated Annual Cost": [f"${df['Updated Annual Cost'].sum():,.2f}"],
        "Subscription Term Total Service Fee": [f"${df['Subscription Term Total Service Fee'].sum():,.2f}"],
        "Monthly Co-Termed Cost": [f"${df['Monthly Co-Termed Cost'].sum():,.2f}"],
        "First Month Co-Termed Cost": [f"${df['First Month Co-Termed Cost'].sum():,.2f}"]
    })
    
    df = pd.concat([df, total_row], ignore_index=True)
    return df, total_prepaid_cost, total_first_year_cost, total_updated_annual_cost, total_subscription_term_fee
