import pandas as pd
import datetime as dt
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

from src.data_loader import load_data
from src.cleaning import clean_data
from src.visualization import save_plot
from src.insights import generate_insights, generate_recommendations
from src.forecasting import forecast_sales

sns.set_style("whitegrid")

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "SuperStoreOrders.csv"
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


# ==============================
# SALES ANALYSIS
# ==============================

def sales_analysis(df):
    total_sales = df['Sales'].sum()
    category_sales = df.groupby('Category')['Sales'].sum()

    fig, ax = plt.subplots()
    sns.barplot(x=category_sales.index, y=category_sales.values, ax=ax)
    ax.set_title("Sales by Category")
    plt.xticks(rotation=45)
    save_plot(fig, "sales_by_category.png")

    category_sales.to_csv(OUTPUT_DIR / "category_sales.csv")

    return total_sales


# ==============================
# RFM ANALYSIS
# ==============================

def rfm_analysis(df):
    snapshot_date = df['Order Date'].max() + dt.timedelta(days=1)

    rfm = df.groupby('Customer Name').agg({
        'Order Date': lambda x: (snapshot_date - x.max()).days,
        'Order ID': 'count',
        'Sales': 'sum'
    })

    rfm.columns = ['Recency', 'Frequency', 'Monetary']

    rfm['R_score'] = pd.qcut(rfm['Recency'], 4, labels=[4,3,2,1], duplicates='drop')
    rfm['F_score'] = pd.qcut(rfm['Frequency'], 4, labels=[1,2,3,4], duplicates='drop')
    rfm['M_score'] = pd.qcut(rfm['Monetary'], 4, labels=[1,2,3,4], duplicates='drop')

    rfm[['R_score','F_score','M_score']] = rfm[['R_score','F_score','M_score']].astype(int)

    rfm['Segment'] = "Others"
    rfm.loc[(rfm['R_score'] == 4) & (rfm['F_score'] == 4), 'Segment'] = "Champions"

    rfm.to_csv(OUTPUT_DIR / "rfm.csv")

    return rfm


# ==============================
# PROFITABILITY ANALYSIS
# ==============================

def profitability_analysis(df):
    profit_sub = df.groupby('Sub-Category')['Profit'].sum().sort_values()

    fig, ax = plt.subplots()
    profit_sub.plot(kind='barh', ax=ax)
    ax.set_title("Profit by Sub-Category")
    save_plot(fig, "profit_subcategory.png")

    # Loss-making products
    loss_products = df.groupby('Product Name')['Profit'].sum().sort_values().head(10)

    fig, ax = plt.subplots()
    loss_products.plot(kind='barh', ax=ax)
    ax.set_title("Top Loss-Making Products")
    save_plot(fig, "loss_products.png")

    loss_products.to_csv(OUTPUT_DIR / "loss_products.csv")


# ==============================
# TIME SERIES + GROWTH
# ==============================

def time_series_analysis(df):
    df['Month'] = df['Order Date'].dt.to_period('M').dt.to_timestamp()

    monthly_sales = df.groupby('Month')['Sales'].sum()
    growth = monthly_sales.pct_change() * 100

    # Monthly sales
    fig, ax = plt.subplots()
    monthly_sales.plot(ax=ax)
    ax.set_title("Monthly Sales Trend")
    save_plot(fig, "monthly_sales.png")

    # Growth
    fig, ax = plt.subplots()
    growth.plot(ax=ax)
    ax.set_title("Monthly Growth (%)")
    save_plot(fig, "monthly_growth.png")


# ==============================
# PRODUCT ANALYSIS
# ==============================

def product_analysis(df):
    top_products = df.groupby('Product Name')['Sales'].sum().sort_values(ascending=False).head(10)

    fig, ax = plt.subplots()
    top_products.plot(kind='barh', ax=ax)
    ax.set_title("Top 10 Products by Sales")
    save_plot(fig, "top_products.png")

    top_products.to_csv(OUTPUT_DIR / "top_products.csv")


# ==============================
# REGION ANALYSIS
# ==============================

def region_analysis(df):
    region = df.groupby('Region').agg({'Sales':'sum','Profit':'sum'})
    region['Profit_Margin'] = (region['Profit'] / region['Sales']) * 100

    fig, ax = plt.subplots()
    region['Profit_Margin'].plot(kind='bar', ax=ax)
    ax.set_title("Profit Margin by Region")
    save_plot(fig, "region_profit_margin.png")

    region.to_csv(OUTPUT_DIR / "region_analysis.csv")


# ==============================
# DISCOUNT ANALYSIS
# ==============================

def discount_analysis(df):
    df['Discount_Bucket'] = pd.cut(
        df['Discount'],
        bins=[0,0.1,0.2,0.3,1],
        labels=['Low','Medium','High','Very High']
    )

    discount_analysis = df.groupby('Discount_Bucket')['Profit'].mean()

    fig, ax = plt.subplots()
    discount_analysis.plot(kind='bar', ax=ax)
    ax.set_title("Avg Profit by Discount Level")
    save_plot(fig, "discount_impact.png")


# ==============================
# MAIN PIPELINE
# ==============================

def run_analysis():
    df = load_data(DATA_PATH)
    df = clean_data(df)

    sales_analysis(df)
    rfm = rfm_analysis(df)
    profitability_analysis(df)
    time_series_analysis(df)
    product_analysis(df)
    region_analysis(df)
    discount_analysis(df)

    # 🔮 Forecast
    prediction = forecast_sales(df)

    generate_insights(df, rfm)
    generate_recommendations(df, rfm)

    print(f"\n📈 Next Month Predicted Sales: {prediction:.2f}")