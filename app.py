import streamlit as st
import pandas as pd
from data import income_statements

# App Config ------------------------------------------------------------------------------------
st.set_page_config(page_title="Client Profitability App", layout="wide")
st.markdown("<h1 style='color:#008B8B; font-weight:bold;'>📊 Client Profitability Consolidator</h1>", unsafe_allow_html=True)

# Product Selection -----------------------------------------------------------------------
product_options = sorted(income_statements.keys())

selected_products = st.sidebar.multiselect(
    "Select products to consolidate:",
    options=product_options,
    default=[product_options[0]])

#### no produced selected handling ---------------------------------------------------------
if not selected_products:
    st.warning("Please select at least one product.")
    st.stop()

# st.sidebar.image("logo.png", use_column_width=True)

# Financial Calculations ------------------------------------------------------------
interest_received = sum(income_statements[p]['interest_received'] for p in selected_products)
cost_of_funds = -sum(income_statements[p]['cost_of_funds'] for p in selected_products)
return_on_capital = sum(income_statements[p]['return_on_capital'] for p in selected_products)
credit_premium = -sum(income_statements[p]['credit_premium'] for p in selected_products)
other_fee_income = sum(income_statements[p]['other_fee_income'] for p in selected_products)
overheads = -sum(income_statements[p]['overheads'] for p in selected_products)
tier1_cost = -sum(income_statements[p]['tier1_cost'] for p in selected_products)
tier2_cost = -sum(income_statements[p]['tier2_cost'] for p in selected_products)
core_equity_cost = -sum(income_statements[p]['core_equity_cost'] for p in selected_products)
capital_holding = sum(income_statements[p]['capital_holding'] for p in selected_products)

gross_lending_margin = interest_received + cost_of_funds
lending_margin_after_credit = gross_lending_margin + return_on_capital + credit_premium
libt = lending_margin_after_credit + other_fee_income + overheads + tier1_cost + tier2_cost
taxation = round(0.27 * libt)
liacc = round(libt * 0.73 + core_equity_cost)
roe = round(((libt * 0.73) / capital_holding) * 100, 2) if capital_holding else 0

metrics = {
    'Interest Received': interest_received,
    'Cost of Funds incl liquids': cost_of_funds,
    'Gross Lending Margin': gross_lending_margin,
    'Return on Capital Invested': return_on_capital,
    'Credit Premium': credit_premium,
    'Lending margin after Credit Premium': lending_margin_after_credit,
    'Other credit based fee income': other_fee_income,
    'Overheads related to lending business': overheads,
    'Additional Tier 1 Cost of Capital': tier1_cost,
    'Tier 2 Cost of Capital': tier2_cost,
    'Lending Income Before Tax( LIBT)': libt,
    'Taxation': taxation,
    'Core Equity Tier 1 Cost Of Capital': core_equity_cost,
    'LIACC': liacc,
    'ROE (Return on Equity)': roe,
    'Core equity capital holding': capital_holding,
}

df_result = pd.DataFrame(list(metrics.items()), columns=["Metric", "Value"])

#------------------------------------------------------------------------------------------------------
# Remove 'Core equity capital holding' if all products are selected
if set(selected_products) == set(product_options):
    df_result = df_result[df_result["Metric"] != "Core equity capital holding"]

#------------------------------------------------------------------------------------------------------------------
# Format numeric values with spaces for thousands
def format_number(row):
    val = row['Value']
    metric = row['Metric']
    
    if metric == 'Cost of Funds incl liquids' and val==0:
        return ""  
    
    if isinstance(val, (int, float)):
        if val == 0:
            return "-" 
        if val == int(val):
            return f"{val:,.0f}".replace(",", " ")
        else: 
            return f"{val:,.2f}".replace(",", " ")
    return val

# df_result["Value"] = df_result.apply(format_number, axis=1)

# Apply Styling ------------------------------------------------------------

highlight_metrics = {
    'ROE (Return on Equity)',
    'Gross Lending Margin',
    'Lending margin after Credit Premium',
    'Lending Income Before Tax( LIBT)',
    'LIACC'
}

def format_value(metric, value):
    if isinstance(value, (int, float)):
        if metric == 'Cost of Funds incl liquids' and value == 0:
            return ""  
        if value == 0:
            return "-"
        if metric == "ROE (Return on Equity)":
            return f"&nbsp;&nbsp;&nbsp;&nbsp;{abs(value):,.2f}%".replace(",", " ")
        if value < 0:
            return f"-&nbsp;&nbsp;&nbsp;&nbsp;{abs(value):,.0f}".replace(",", " ").rjust(10).replace(' ', '&nbsp;')
        return f"&nbsp;&nbsp;&nbsp;&nbsp;{value:,.0f}".replace(",", " ").rjust(10).replace(' ', '&nbsp;')
    return value


def make_row(metric, value):
    color = "#c6efce" if metric == "ROE (Return on Equity)" else "#fff4e6" if metric in highlight_metrics else ""
    if metric in highlight_metrics:
        metric_html = f"<b>{metric}</b>"
        value_html = f"<b>{value}</b>"
    else:
        metric_html = metric
        value_html = value

    row_style = f' style="background-color:{color}"' if color else ""
    return f"<tr{row_style}><td>{metric_html}</td><td style='text-align:right'>{value_html}</td></tr>"

# Generate a list of HTML-formatted table rows from the dtaframe
rows = [
    make_row(row['Metric'], format_value(row['Metric'], row['Value']))
    for _, row in df_result.iterrows()]


column_label = selected_products[0] if len(selected_products) == 1 else "Value"

html_table = f"""
<table style="width:100%; border-collapse: collapse">
    <thead>
        <tr style="background-color:#f0f0f0">
            <th style="text-align:left"></th>
            <th style="text-align:right">{column_label}</th>
        </tr>
    </thead>
    <tbody>
        {''.join(rows)}
    </tbody>
</table>
"""

st.markdown("#### Consolidated Income Statement", unsafe_allow_html=True) #show table
st.markdown(html_table, unsafe_allow_html=True)

##### End ------------------------------------------------------------------------------------------------------------------
