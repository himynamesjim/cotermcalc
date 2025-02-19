import streamlit as st
import pandas as pd

def calculate_costs(df, agreement_term, months_remaining, payment_model):
    months_elapsed = agreement_term - months_remaining
    total_annual_cost = 0
    total_prepaid_cost = 0
    total_first_year_cost = 0
    
    for index, row in df.iterrows():
        annual_total_fee = row['Unit Quantity'] * row['Annual Unit Fee']
        subscription_term_total_fee = (annual_total_fee * months_remaining) / 12
        co_termed_prepaid_cost = (row['Additional Licenses'] * row['Annual Unit Fee'] * months_remaining) / 12 if payment_model == 'Prepaid' else 0
        co_termed_first_year_cost = (row['Additional Licenses'] * row['Annual Unit Fee'] * (12 - (months_elapsed % 12))) / 12 if payment_model == 'Annual' else 0
        updated_annual_cost = annual_total_fee + (row['Additional Licenses'] * row['Annual Unit Fee']) if payment_model == 'Annual' else 0
        
        df.at[index, 'Annual Total Services Fee'] = annual_total_fee
        df.at[index, 'Subscription Term Total Service Fee'] = subscription_term_total_fee
        df.at[index, 'Prepaid Co-Termed Cost'] = co_termed_prepaid_cost
        df.at[index, 'First Year Co-Termed Cost'] = co_termed_first_year_cost
        df.at[index, 'Updated Annual Cost'] = updated_annual_cost
        
        total_annual_cost += updated_annual_cost
        total_prepaid_cost += co_termed_prepaid_cost
        total_first_year_cost += co_termed_first_year_cost
    
    return df, total_prepaid_cost, total_first_year_cost, total_annual_cost

st.title("Co-Terming Cost Calculator")

agreement_term = st.number_input("Agreement Term (Months):", min_value=1, value=36)
months_remaining = st.number_input("Months Remaining:", min_value=1, max_value=agreement_term, value=30)
payment_model = st.selectbox("Payment Model:", ["Prepaid", "Annual"])

st.subheader("Enter License Information")
num_items = st.number_input("Number of Line Items:", min_value=1, value=1)

columns = ["Cloud Service Description", "Unit Quantity", "Annual Unit Fee", "Additional Licenses", "Annual Total Services Fee", "Subscription Term Total Service Fee", "Prepaid Co-Termed Cost", "First Year Co-Termed Cost", "Updated Annual Cost"]
data = pd.DataFrame(columns=columns)

for i in range(num_items):
    service_name = st.text_input(f"Cloud Service Description (Item {i+1}):")
    unit_quantity = st.number_input(f"Unit Quantity (Item {i+1}):", min_value=0, value=0)
    annual_fee = st.number_input(f"Annual Unit Fee ($) (Item {i+1}):", min_value=0.0, value=0.0)
    additional_licenses = st.number_input(f"Additional Licenses (Item {i+1}):", min_value=0, value=0)
    
    new_row = pd.DataFrame({
        "Cloud Service Description": [service_name],
        "Unit Quantity": [unit_quantity],
        "Annual Unit Fee": [annual_fee],
        "Additional Licenses": [additional_licenses],
        "Annual Total Services Fee": [0],
        "Subscription Term Total Service Fee": [0],
        "Prepaid Co-Termed Cost": [0],
        "First Year Co-Termed Cost": [0],
        "Updated Annual Cost": [0]
    })
    data = pd.concat([data, new_row], ignore_index=True)

if st.button("Calculate Costs"):
    data, total_prepaid, total_first_year, total_annual = calculate_costs(data, agreement_term, months_remaining, payment_model)
    st.subheader("Results")
    st.write(f"Months Elapsed: {agreement_term - months_remaining}")
    st.write(f"Pre-Paid Co-Termed Cost: ${total_prepaid:.2f}") if payment_model == "Prepaid" else st.write("Pre-Paid Co-Termed Cost: $0.00")
    st.write(f"First Year Co-Termed Cost: ${total_first_year:.2f}") if payment_model == "Annual" else st.write("First Year Co-Termed Cost: $0.00")
    st.write(f"Total Annual Cost for Remaining Years: ${total_annual:.2f}") if payment_model == "Annual" else st.write("Total Annual Cost for Remaining Years: $0.00")
    
    st.subheader("Detailed Line Items")
    st.dataframe(data)
