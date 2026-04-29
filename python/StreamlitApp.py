import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import os

# ==============================
# Page Config
# ==============================
st.set_page_config(page_title="Retail Dashboard", layout="wide")

# ==============================
# Theme Toggle
# ==============================
mode = st.sidebar.radio("Theme", ["Light", "Dark"])
template = "plotly_dark" if mode == "Dark" else "plotly"

st.title("🛒 Retail Sales Dashboard (Interactive)")

# ==============================
# Load Data (robust path)
# ==============================
@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, 'data', 'SuperStoreOrders.csv')
    df = pd.read_csv(file_path, encoding='utf-8-sig')
    df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True)

    df['Sales'] = pd.to_numeric(df['Sales'].astype(str).str.replace(',', ''), errors='coerce')
    for col in ['Profit', 'Discount', 'Shipping Cost']:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')

    return df


df = load_data()

# ==============================
# Filters
# ==============================
st.sidebar.header("🔎 Filters")
region = st.sidebar.multiselect("Region", df['Region'].unique(), default=df['Region'].unique())
category = st.sidebar.multiselect("Category", df['Category'].unique(), default=df['Category'].unique())

min_date = df['Order Date'].min()
max_date = df['Order Date'].max()
date_range = st.sidebar.date_input("Date Range", [min_date, max_date])

filtered_df = df[
    (df['Region'].isin(region)) &
    (df['Category'].isin(category)) &
    (df['Order Date'] >= pd.to_datetime(date_range[0])) &
    (df['Order Date'] <= pd.to_datetime(date_range[1]))
]

# ==============================
# KPIs
# ==============================
col1, col2, col3 = st.columns(3)
col1.metric("💰 Sales", f"${filtered_df['Sales'].sum():,.0f}")
col2.metric("📈 Profit", f"${filtered_df['Profit'].sum():,.0f}")
col3.metric("📦 Orders", filtered_df['Order ID'].nunique())

# ==============================
# AI Insights
# ==============================
def generate_insights(df):
    insights = []

    if df.empty:
        return ["No data available for selected filters."]

    total_sales = df['Sales'].sum()

    # Category
    cat_sales = df.groupby('Category')['Sales'].sum()
    top_cat = cat_sales.idxmax()
    pct = (cat_sales.max() / total_sales) * 100
    insights.append(f"{top_cat} is the top-performing category contributing {pct:.1f}% of total sales.")

    # Region
    reg_sales = df.groupby('Region')['Sales'].sum()
    top_reg = reg_sales.idxmax()
    insights.append(f"{top_reg} region generates the highest sales.")

    # Loss-making sub-category
    sub_profit = df.groupby('Sub-Category')['Profit'].sum()
    worst = sub_profit.idxmin()
    insights.append(f"{worst} is the most loss-making sub-category.")

    # Discount correlation
    corr = df[['Discount', 'Profit']].corr().iloc[0,1]
    if corr < -0.3:
        insights.append("Higher discounts are significantly reducing profit.")
    elif corr < 0:
        insights.append("Discounts slightly reduce profitability.")
    else:
        insights.append("Discounts are not significantly hurting profits.")

    return insights

st.markdown("---")
st.subheader("🧠 AI-Generated Insights")
st.info("Insights update automatically based on filters")

for insight in generate_insights(filtered_df):
    st.markdown(f"• {insight}")

# ==============================
# Downloads
# ==============================
def to_csv(df): return df.to_csv(index=False).encode('utf-8')

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# ==============================
# Charts (Plotly)
# ==============================

# Sales by Category
st.subheader("📊 Sales by Category")
category_sales = filtered_df.groupby('Category')['Sales'].sum().reset_index()
fig1 = px.bar(category_sales, x='Category', y='Sales', template=template)
st.plotly_chart(fig1, use_container_width=True)

# Profit by Sub-Category
st.subheader("📉 Profit by Sub-Category")
profit_sub = filtered_df.groupby('Sub-Category')['Profit'].sum().reset_index()
fig2 = px.bar(profit_sub, x='Profit', y='Sub-Category', orientation='h', template=template)
st.plotly_chart(fig2, use_container_width=True)

# Monthly Trend
st.subheader("📅 Monthly Sales Trend")
filtered_df['Month-Year'] = filtered_df['Order Date'].dt.to_period('M').astype(str)
monthly = filtered_df.groupby('Month-Year')['Sales'].sum().reset_index()
fig3 = px.line(monthly, x='Month-Year', y='Sales', template=template)
st.plotly_chart(fig3, use_container_width=True)

# Scatter
st.subheader("⚖️ Discount vs Profit")
fig4 = px.scatter(filtered_df, x='Discount', y='Profit', template=template)
st.plotly_chart(fig4, use_container_width=True)

# ==============================
# Map
# ==============================
st.subheader("🌍 Sales by Country")
country_sales = filtered_df.groupby('Country')['Sales'].sum().reset_index()
fig_map = px.choropleth(country_sales,
                        locations='Country',
                        locationmode='country names',
                        color='Sales',
                        template=template)
st.plotly_chart(fig_map, use_container_width=True)

# ==============================
# RFM
# ==============================
st.subheader("🧠 Customer Segments")
snapshot_date = filtered_df['Order Date'].max() + pd.Timedelta(days=1)

rfm = filtered_df.groupby('Customer Name').agg({
    'Order Date': lambda x: (snapshot_date - x.max()).days,
    'Order ID': 'count',
    'Sales': 'sum'
}).reset_index()

rfm.columns = ['Customer Name', 'Recency', 'Frequency', 'Monetary']

rfm['R_score'] = pd.qcut(rfm['Recency'], 4, labels=[4,3,2,1], duplicates='drop')
rfm['F_score'] = pd.qcut(rfm['Frequency'], 4, labels=[1,2,3,4], duplicates='drop')
rfm['M_score'] = pd.qcut(rfm['Monetary'], 4, labels=[1,2,3,4], duplicates='drop')

rfm['Segment'] = rfm['R_score'].astype(str) + rfm['F_score'].astype(str) + rfm['M_score'].astype(str)

seg_counts = rfm['Segment'].value_counts().reset_index()
seg_counts.columns = ['Segment', 'Count']

fig5 = px.bar(seg_counts, x='Segment', y='Count', template=template)
st.plotly_chart(fig5, use_container_width=True)

st.download_button("⬇️ Download RFM CSV", to_csv(rfm), "rfm.csv")

# ==============================
# Top Customers
# ==============================
st.subheader("🏆 Top Customers")
top = rfm.sort_values(by='Monetary', ascending=False).head(10)
st.dataframe(top)

# ==============================
# Full Data Download
# ==============================
st.download_button("⬇️ Download Filtered Data", to_csv(filtered_df), "filtered_data.csv")

