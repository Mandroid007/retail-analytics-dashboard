import pandas as pd
import streamlit as st
import plotly.express as px

st.title("Retail Analytics Test Dashboard")

# Load CSVs
products = pd.read_csv("Products.csv")
customers = pd.read_csv("Customers.csv")
sales = pd.read_csv("Sales.csv")


# ----------------------
products.columns = products.columns.str.strip()
customers.columns = customers.columns.str.strip()
sales.columns = sales.columns.str.strip()

# ----------------------
# Step 3: Merge Sales with Products and Customers
# ----------------------
data = sales.merge(products, on="Product_ID").merge(customers, on="Customer_ID")

# ----------------------
# Step 4: Rename columns for clarity
# ----------------------
data.rename(columns={
    "Customer_Type_y": "Customer_Type",
    "Cost_Price_y": "Cost_Price"
}, inplace=True)

# ----------------------
# Step 5: Calculate Revenue, Profit, Profit Margin
# ----------------------
data["Revenue"] = data["Quantity"] * data["Selling_Price"]
data["Profit"] = data["Quantity"] * (data["Selling_Price"] - data["Cost_Price"])
data["Profit_Margin"] = (data["Profit"] / data["Revenue"]) * 100

# ----------------------
# Step 6: Convert Date column to datetime
# ----------------------
data["Date"] = pd.to_datetime(data["Date"])
data["Year"] = data["Date"].dt.year
data["Month"] = data["Date"].dt.month_name()

# ----------------------
# Step 7: Streamlit Layout
# ----------------------
st.set_page_config(page_title="RetailAnalytics Dashboard", layout="wide")
st.title("RetailAnalytics Interactive Dashboard")

# ----------------------
# Sidebar Filters
# ----------------------
years = st.sidebar.multiselect("Select Year(s):", options=data["Year"].unique(), default=data["Year"].unique())
months = st.sidebar.multiselect("Select Month(s):", options=data["Month"].unique(), default=data["Month"].unique())
products_selected = st.sidebar.multiselect("Select Product(s):", options=data["Product_Name"].unique(), default=data["Product_Name"].unique())
customers_selected = st.sidebar.multiselect("Select Customer Type(s):", options=data["Customer_Type"].unique(), default=data["Customer_Type"].unique())

# Filter data
filtered_data = data[
    (data["Year"].isin(years)) &
    (data["Month"].isin(months)) &
    (data["Product_Name"].isin(products_selected)) &
    (data["Customer_Type"].isin(customers_selected))
]

# ----------------------
# Key Metrics
# ----------------------
st.subheader("Key Metrics")
total_revenue = filtered_data["Revenue"].sum()
total_profit = filtered_data["Profit"].sum()
avg_margin = filtered_data["Profit_Margin"].mean()

col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue", f"₦{total_revenue:,.2f}")
col2.metric("Total Profit", f"₦{total_profit:,.2f}")
col3.metric("Average Profit Margin", f"{avg_margin:.2f}%")

# ----------------------
# Revenue by Product
# ----------------------
st.subheader("Revenue by Product")
revenue_chart = px.bar(
    filtered_data.groupby("Product_Name")["Revenue"].sum().reset_index(),
    x="Product_Name",
    y="Revenue",
    text_auto=True,
    title="Revenue by Product",
    color="Revenue",
    color_continuous_scale="Viridis"
)
st.plotly_chart(revenue_chart, use_container_width=True)

# ----------------------
# Profit by Customer Type
# ----------------------
st.subheader("Profit by Customer Type")
profit_chart = px.bar(
    filtered_data.groupby("Customer_Type")["Profit"].sum().reset_index(),
    x="Customer_Type",
    y="Profit",
    text_auto=True,
    color="Profit",
    color_continuous_scale="Cividis"
)
st.plotly_chart(profit_chart, use_container_width=True)

# ----------------------
# Monthly Profit Trend
# ----------------------
st.subheader("Monthly Profit Trend")
monthly_profit = filtered_data.groupby(filtered_data["Date"].dt.to_period("M"))["Profit"].sum().reset_index()
monthly_profit["Date"] = monthly_profit["Date"].dt.to_timestamp()
profit_trend = px.line(monthly_profit, x="Date", y="Profit", markers=True, title="Monthly Profit Trend")
st.plotly_chart(profit_trend, use_container_width=True)

# ----------------------
# Top 3 Products by Revenue
# ----------------------
st.subheader("Top 3 Products by Revenue")
top_products = filtered_data.groupby("Product_Name")["Revenue"].sum().sort_values(ascending=False).head(3).reset_index()
st.dataframe(top_products)

st.subheader("Download Filtered Data")
csv = filtered_data.to_csv(index=False).encode('utf-8')
st.download_button(label="Download CSV", data=csv, file_name='filtered_retail_data.csv', mime='text/csv')
