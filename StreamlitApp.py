import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

from src.cleaning import clean_data

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(
    page_title="Retail Sales Dashboard",
    layout="wide",
    page_icon="📊"
)

st.title("📊 Retail Sales Dashboard")
st.caption("Advanced Business Intelligence • Forecasting • Strategic Recommendations")

# ==============================
# PATHS
# ==============================
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "SuperStoreOrders.csv"
OUTPUT_PATH = BASE_DIR / "outputs"

# ==============================
# LOAD DATA
# ==============================
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    return clean_data(df)

df = load_data()

# ==============================
# SIDEBAR FILTERS
# ==============================
st.sidebar.header("🔍 Advanced Filters")

min_date = df['Order Date'].min()
max_date = df['Order Date'].max()

start_date, end_date = st.sidebar.slider(
    "Order Date Range",
    min_value=min_date.to_pydatetime(),
    max_value=max_date.to_pydatetime(),
    value=(min_date.to_pydatetime(), max_date.to_pydatetime())
)

category = st.sidebar.multiselect(
    "Category",
    sorted(df['Category'].dropna().unique()),
    default=sorted(df['Category'].dropna().unique())
)

region = st.sidebar.multiselect(
    "Region",
    sorted(df['Region'].dropna().unique()),
    default=sorted(df['Region'].dropna().unique())
)

segment = st.sidebar.multiselect(
    "Segment",
    sorted(df['Segment'].dropna().unique()),
    default=sorted(df['Segment'].dropna().unique())
)

ship_mode = st.sidebar.multiselect(
    "Ship Mode",
    sorted(df['Ship Mode'].dropna().unique()),
    default=sorted(df['Ship Mode'].dropna().unique())
)

state = st.sidebar.multiselect(
    "State",
    sorted(df['State'].dropna().unique()),
    default=sorted(df['State'].dropna().unique())
)

discount_range = st.sidebar.slider(
    "Discount Range",
    float(df['Discount'].min()),
    float(df['Discount'].max()),
    (float(df['Discount'].min()), float(df['Discount'].max()))
)

sales_range = st.sidebar.slider(
    "Sales Range",
    float(df['Sales'].min()),
    float(df['Sales'].max()),
    (float(df['Sales'].min()), float(df['Sales'].max()))
)

search_product = st.sidebar.text_input("🔎 Search Product")

# ==============================
# FILTER DATA
# ==============================
filtered_df = df[
    (df['Order Date'] >= pd.to_datetime(start_date)) &
    (df['Order Date'] <= pd.to_datetime(end_date)) &
    (df['Category'].isin(category)) &
    (df['Region'].isin(region)) &
    (df['Segment'].isin(segment)) &
    (df['Ship Mode'].isin(ship_mode)) &
    (df['State'].isin(state)) &
    (df['Discount'] >= discount_range[0]) &
    (df['Discount'] <= discount_range[1]) &
    (df['Sales'] >= sales_range[0]) &
    (df['Sales'] <= sales_range[1])
]

if search_product:
    filtered_df = filtered_df[
        filtered_df['Product Name'].fillna('').str.contains(search_product, case=False)
    ]

if filtered_df.empty:
    st.warning("⚠️ No data available for selected filters")
    st.stop()

# ==============================
# PREVIOUS PERIOD
# ==============================
def calculate_previous_period(df, start_date, end_date):
    delta = end_date - start_date
    return df[
        (df['Order Date'] >= start_date - delta) &
        (df['Order Date'] < start_date)
    ]

prev_df = calculate_previous_period(df, pd.to_datetime(start_date), pd.to_datetime(end_date))

# ==============================
# KPI METRICS
# ==============================
def growth(curr, prev):
    return ((curr - prev) / prev * 100) if prev else 0

total_sales = filtered_df['Sales'].sum()
total_profit = filtered_df['Profit'].sum()
avg_discount = filtered_df['Discount'].mean()
profit_margin = total_profit / total_sales if total_sales else 0

sales_growth = growth(total_sales, prev_df['Sales'].sum())
profit_growth = growth(total_profit, prev_df['Profit'].sum())

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Sales", f"{total_sales:,.0f}", f"{sales_growth:.2f}%")
col2.metric("📈 Total Profit", f"{total_profit:,.0f}", f"{profit_growth:.2f}%")
col3.metric("🎯 Avg Discount", f"{avg_discount:.2%}")
col4.metric("📊 Profit Margin", f"{profit_margin:.2%}")

st.markdown("---")

# ==============================
# TABS
# ==============================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Sales",
    "📦 Products",
    "👥 Customers",
    "🌍 Region",
    "🔮 Forecast",
    "🧠 Insights"
])

# ==============================
# SALES TAB
# ==============================
with tab1:
    filtered_df['Month'] = filtered_df['Order Date'].dt.to_period('M').dt.to_timestamp()
    monthly_sales = filtered_df.groupby('Month')['Sales'].sum().reset_index()

    fig = px.line(monthly_sales, x='Month', y='Sales', markers=True, title="Monthly Sales Trend")
    st.plotly_chart(fig, use_container_width=True)

    monthly_sales['MoM Growth %'] = monthly_sales['Sales'].pct_change() * 100
    fig_growth = px.bar(monthly_sales, x='Month', y='MoM Growth %', title="Month-over-Month Sales Growth")
    st.plotly_chart(fig_growth, use_container_width=True)

    fig_discount = px.scatter(
        filtered_df,
        x='Discount',
        y='Profit',
        color='Category',
        size='Sales',
        title='Discount vs Profit Leakage'
    )
    st.plotly_chart(fig_discount, use_container_width=True)

# ==============================
# PRODUCTS TAB
# ==============================
with tab2:
    product_data = filtered_df.groupby(['Category', 'Sub-Category']).agg({
        'Sales':'sum',
        'Profit':'sum'
    }).reset_index()

    fig_tree = px.treemap(
        product_data,
        path=['Category', 'Sub-Category'],
        values='Sales',
        color='Profit',
        title='Category/Sub-Category Performance'
    )
    st.plotly_chart(fig_tree, use_container_width=True)

# ==============================
# CUSTOMERS TAB
# ==============================
with tab3:
    segment_data = filtered_df.groupby('Segment').agg({
        'Sales':'sum',
        'Profit':'sum'
    }).reset_index()

    fig_segment = px.bar(
        segment_data,
        x='Segment',
        y='Sales',
        color='Profit',
        title='Customer Segment Performance'
    )
    st.plotly_chart(fig_segment, use_container_width=True)

# ==============================
# REGION TAB
# ==============================
with tab4:
    region_data = filtered_df.groupby('Region').agg({
        'Sales':'sum',
        'Profit':'sum'
    }).reset_index()

    # 🔥 SORT by Sales (descending)
    region_data = region_data.sort_values(by='Sales', ascending=True)

    fig_region = px.bar(
        region_data,
        x='Sales',
        y='Region',
        orientation='h',
        color='Profit',
        title='Regional Sales & Profitability'
    )

    st.plotly_chart(fig_region, use_container_width=True)

# ==============================
# FORECAST TAB
# ==============================
with tab5:
    forecast_file = OUTPUT_PATH / "sales_forecast.csv"

    if forecast_file.exists():
        forecast_df = pd.read_csv(forecast_file)
        pred = float(forecast_df.iloc[0,0])

        fig_forecast = px.line(monthly_sales, x='Month', y='Sales', title='Sales Forecast')
        fig_forecast.add_scatter(
            x=[monthly_sales['Month'].max()],
            y=[pred],
            mode='markers+text',
            text=[f'Forecast: {pred:,.0f}'],
            name='Forecast'
        )
        st.plotly_chart(fig_forecast, use_container_width=True)

# ==============================
# SMART INSIGHTS TAB
# ==============================
with tab6:
    st.subheader("🧠 Strategic Insights & Recommendations")

    top_region = filtered_df.groupby('Region')['Sales'].sum().idxmax()
    low_profit_region = filtered_df.groupby('Region')['Profit'].sum().idxmin()
    top_category = filtered_df.groupby('Category')['Sales'].sum().idxmax()
    best_segment = filtered_df.groupby('Segment')['Profit'].sum().idxmax()
    risky_products = filtered_df.groupby('Product Name')['Profit'].sum().nsmallest(5)

    st.write(f"• Highest sales region: **{top_region}**")
    st.write(f"• Lowest profit region: **{low_profit_region}**")
    st.write(f"• Best performing category: **{top_category}**")
    st.write(f"• Most profitable customer segment: **{best_segment}**")

    if avg_discount > 0.3:
        st.warning("⚠️ High discounts detected → Review discount strategy to protect margins")

    if profit_margin < 0.1:
        st.warning("⚠️ Low profit margin → Consider pricing optimization")

    st.write("### 🚨 Top 5 Loss-Making Products")
    st.dataframe(risky_products.reset_index().rename(columns={0:'Profit'}))

    st.write("### 📌 Strategic Recommendations")

    recommendations = []

    if avg_discount > 0.3:
        recommendations.append("Reduce excessive discounting in low-margin categories.")

    if low_profit_region:
        recommendations.append(f"Investigate operational inefficiencies in {low_profit_region} region.")

    if profit_margin < 0.1:
        recommendations.append("Reassess product pricing and supplier costs.")

    if len(recommendations) == 0:
        recommendations.append("Current performance appears healthy. Focus on scaling top-performing categories.")

    for rec in recommendations:
        st.success(f"• {rec}")

# ==============================
# DOWNLOAD
# ==============================
csv = filtered_df.to_csv(index=False).encode('utf-8')

st.download_button(
    "📥 Download Filtered Data",
    csv,
    "filtered_sales_data.csv",
    "text/csv"
)

# ==============================
# RAW DATA
# ==============================
with st.expander("📊 View Raw Data"):
    st.dataframe(filtered_df, use_container_width=True)
