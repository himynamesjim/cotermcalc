import streamlit as st
import pandas as pd

def calculate_costs(df, agreement_term, months_remaining, payment_model):
    months_elapsed = agreement_term - months_remaining
    total_annual_cost = 0
    total_prepaid_cost = 0
    total_first_year_cost = 0
    total_annual_unit_fee = 0
    total_subscription_term_fee = 0
    total_updated_annual_cost = 0
    total_current_annual_services_fee = 0
    total_prepaid_total_cost = 0
    
    for index, row in df.iterrows():
        annual_total_fee = row['Unit Quantity'] * row['Annual Unit Fee']
        subscription_term_total_fee = ((annual_total_fee * months_remaining) / 12) + ((row['Additional Licenses'] * row['Annual Unit Fee'] * months_remaining) / 12)
        co_termed_prepaid_cost = (row['Additional Licenses'] * row['Annual Unit Fee'] * months_remaining) / 12 if payment_model == 'Prepaid' else 0
        co_termed_first_year_cost = (row['Additional Licenses'] * row['Annual Unit Fee'] * (12 - (months_elapsed % 12))) / 12 if payment_model == 'Annual' else 0
        updated_annual_cost = annual_total_fee + (row['Additional Licenses'] * row['Annual Unit Fee']) if payment_model == 'Annual' else 0
        
        df.at[index, 'Annual Unit Fee'] = f"${row['Annual Unit Fee']:,.2f}"
        df.at[index, 'Current Annual Total Services Fee'] = f"${annual_total_fee:,.2f}"
        df.at[index, 'Prepaid Co-Termed Cost'] = f"${co_termed_prepaid_cost:,.2f}"
        df.at[index, 'First Year Co-Termed Cost'] = f"${co_termed_first_year_cost:,.2f}"
        df.at[index, 'Updated Annual Cost'] = f"${updated_annual_cost:,.2f}"
        df.at[index, 'Subscription Term Total Service Fee'] = f"${subscription_term_total_fee:,.2f}"
        
        total_annual_cost += updated_annual_cost
        total_prepaid_cost += co_termed_prepaid_cost
        total_first_year_cost += co_termed_first_year_cost
        total_annual_unit_fee += row['Annual Unit Fee']
        total_subscription_term_fee += subscription_term_total_fee
        total_updated_annual_cost += updated_annual_cost
        total_current_annual_services_fee += annual_total_fee
        total_prepaid_total_cost += co_termed_prepaid_cost
    
    return df, total_prepaid_cost, total_first_year_cost, total_annual_cost, total_annual_unit_fee, total_subscription_term_fee, total_updated_annual_cost, total_current_annual_services_fee, total_prepaid_total_cost

st.title("Co-Terming Cost Calculator")

st.subheader("Input Form")
customer_name = st.text_input("Customer Name:")
agreement_term = st.number_input("Agreement Term (Months):", min_value=1, value=36, step=1, format="%d")
months_remaining = st.number_input("Months Remaining:", min_value=0.01, max_value=float(agreement_term), value=30.0, step=0.01, format="%.2f")
payment_model = st.selectbox("Payment Model:", ["Prepaid", "Annual"])
num_items = st.number_input("Number of Line Items:", min_value=1, value=1, step=1, format="%d")

st.subheader("Enter License Information")
columns = ["Cloud Service Description", "Unit Quantity", "Annual Unit Fee", "Additional Licenses", "Current Annual Total Services Fee", "Prepaid Co-Termed Cost", "First Year Co-Termed Cost", "Updated Annual Cost", "Subscription Term Total Service Fee"]
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
    data, total_prepaid, total_first_year, total_annual, total_annual_unit_fee, total_subscription_term_fee, total_updated_annual_cost, total_current_annual_services_fee, total_prepaid_total_cost = calculate_costs(data, agreement_term, months_remaining, payment_model)
    
    st.markdown(f"### Customer Name: {customer_name}")
    st.markdown(f"### Months Elapsed: {agreement_term - months_remaining:.2f}")
    st.markdown(f"### Pre-Paid Co-Termed Cost: ${total_prepaid:,.2f}" if payment_model == "Prepaid" else "### Pre-Paid Co-Termed Cost: $0.00")
    st.markdown(f"### First Year Co-Termed Cost: ${total_first_year:,.2f}" if payment_model == "Annual" else "### First Year Co-Termed Cost: $0.00")
    st.markdown(f"### Total Annual Cost for Remaining Years: ${total_annual:,.2f}" if payment_model == "Annual" else "### Total Annual Cost for Remaining Years: $0.00")
    st.markdown(f"### Total Pre-Paid Cost: ${total_prepaid_total_cost:,.2f}")
    
    st.subheader("Detailed Line Items")
    total_row = pd.DataFrame({
        "Cloud Service Description": ["Total Services Cost"],
        "Unit Quantity": ["-"],
        "Annual Unit Fee": [f"${total_annual_unit_fee:,.2f}"],
        "Additional Licenses": ["-"],
        "Current Annual Total Services Fee": [f"${total_current_annual_services_fee:,.2f}"],
        "Prepaid Co-Termed Cost": [f"${total_prepaid_total_cost:,.2f}"],
        "First Year Co-Termed Cost": [f"${total_first_year:,.2f}"],
        "Updated Annual Cost": [f"${total_updated_annual_cost:,.2f}"],
        "Subscription Term Total Service Fee": [f"${total_subscription_term_fee:,.2f}"]
    })
    data = pd.concat([data, total_row], ignore_index=True)
    st.dataframe(data)
