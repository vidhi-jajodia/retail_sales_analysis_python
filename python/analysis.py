import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ==============================
# Setup
# ==============================

# Create folders
os.makedirs('outputs', exist_ok=True)
os.makedirs('screenshots', exist_ok=True)

# Style
sns.set_style("whitegrid")

# ==============================
# Load dataset
# ==============================

df = pd.read_csv('data/SuperStoreOrders.csv', encoding='utf-8-sig')

print(df.head())
print(df.columns)
print(df.info())
print(df.isnull().sum())

# ==============================
# Data Cleaning
# ==============================

# Convert dates
df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True)

# Remove duplicates
df = df.drop_duplicates()

# Clean numeric columns
df['Sales'] = df['Sales'].astype(str).str.replace(',', '')
df['Sales'] = pd.to_numeric(df['Sales'], errors='coerce')

for col in ['Profit', 'Discount', 'Shipping Cost']:
    df[col] = df[col].astype(str).str.replace(',', '')
    df[col] = pd.to_numeric(df[col], errors='coerce')

print("Cleaned data shape:", df.shape)

# ==============================
# Sales Analysis
# ==============================

total_sales = df['Sales'].sum()
print("Total Sales:", total_sales)

category_sales = df.groupby('Category')['Sales'].sum()
print(category_sales)

# Plot: Sales by Category
plt.figure(figsize=(8,5))
sns.barplot(x=category_sales.index, y=category_sales.values)
plt.title('Sales by Category')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('screenshots/sales_by_category.png')
plt.show()
plt.close()

# Save output
category_sales.to_csv('outputs/category_sales.csv')

# ==============================
# RFM Analysis
# ==============================

snapshot_date = df['Order Date'].max() + dt.timedelta(days=1)

rfm = df.groupby('Customer Name').agg({
    'Order Date': lambda x: (snapshot_date - x.max()).days,
    'Order ID': 'count',
    'Sales': 'sum'
})

rfm.columns = ['Recency', 'Frequency', 'Monetary']
print(rfm.head())

# RFM Scores
rfm['R_score'] = pd.qcut(rfm['Recency'], 4, labels=[4,3,2,1])
rfm['F_score'] = pd.qcut(rfm['Frequency'], 4, labels=[1,2,3,4])
rfm['M_score'] = pd.qcut(rfm['Monetary'], 4, labels=[1,2,3,4])

rfm['RFM_Score'] = (
    rfm['R_score'].astype(str) +
    rfm['F_score'].astype(str) +
    rfm['M_score'].astype(str)
)

# Segmentation
def segment(row):
    if row['RFM_Score'] == '444':
        return 'Champions'
    elif row['R_score'] >= 3 and row['F_score'] >= 3:
        return 'Loyal Customers'
    elif row['R_score'] == 4:
        return 'Recent Customers'
    elif row['M_score'] == 4:
        return 'Big Spenders'
    else:
        return 'At Risk'

rfm['Segment'] = rfm.apply(segment, axis=1)

print(rfm['Segment'].value_counts())

# Plot: Customer Segments
plt.figure(figsize=(8,5))
rfm['Segment'].value_counts().plot(kind='bar', title='Customer Segments')
plt.tight_layout()
plt.savefig('screenshots/customer_segments.png')
plt.show()
plt.close()

# Save RFM
rfm.to_csv('outputs/rfm_analysis.csv')

# ==============================
# Profitability Analysis
# ==============================

profit_category = df.groupby('Category')['Profit'].sum().sort_values(ascending=False)
profit_subcategory = df.groupby('Sub-Category')['Profit'].sum().sort_values()

print(profit_category)
print(profit_subcategory)

# Plot: Profit by Sub-Category
plt.figure(figsize=(8,6))
profit_subcategory.plot(kind='barh', title='Profit by Sub-Category')
plt.tight_layout()
plt.savefig('screenshots/profit_subcategory.png')
plt.show()
plt.close()

# Correlation Plot
print(df[['Discount', 'Profit']].corr())

plt.figure(figsize=(8,5))
sns.scatterplot(x='Discount', y='Profit', data=df)
plt.title('Discount vs Profit')
plt.tight_layout()
plt.savefig('screenshots/discount_vs_profit.png')
plt.show()
plt.close()

# ==============================
# Regional Analysis
# ==============================

region_sales = df.groupby('Region')['Sales'].sum()
region_profit = df.groupby('Region')['Profit'].sum()

print(region_sales)
print(region_profit)

# Plot: Sales by Region
plt.figure(figsize=(8,5))
region_sales.plot(kind='bar', title='Sales by Region')
plt.tight_layout()
plt.savefig('screenshots/region_sales.png')
plt.show()
plt.close()

# Plot: Profit by Region
plt.figure(figsize=(8,5))
region_profit.plot(kind='bar', title='Profit by Region')
plt.tight_layout()
plt.savefig('screenshots/region_profit.png')
plt.show()
plt.close()

# ==============================
# Time Series Analysis
# ==============================

df['Month-Year'] = df['Order Date'].dt.to_period('M')
monthly_sales = df.groupby('Month-Year')['Sales'].sum()

plt.figure(figsize=(10,5))
monthly_sales.plot(title='Monthly Sales Trend')
plt.tight_layout()
plt.savefig('screenshots/monthly_sales.png')
plt.show()
plt.close()

# ==============================
# Top Insights
# ==============================

# Top customers
top_customers = rfm.sort_values(by='Monetary', ascending=False).head(10)
print(top_customers)
top_customers.to_csv('outputs/top_customers.csv')

# Loss-making products
loss_products = df.groupby('Product Name')['Profit'].sum().sort_values().head(10)
print(loss_products)
loss_products.to_csv('outputs/loss_products.csv')

# Save outputs
profit_category.to_csv('outputs/profit_category.csv')
profit_subcategory.to_csv('outputs/profit_subcategory.csv')
region_sales.to_csv('outputs/region_sales.csv')

print("✅ Analysis complete. Outputs and screenshots saved.")