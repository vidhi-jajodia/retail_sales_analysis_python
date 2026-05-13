from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


def generate_insights(df, rfm):
    insights = []

    # =========================
    # Revenue concentration
    # =========================
    top_10 = rfm.sort_values(by='Monetary', ascending=False).head(10)
    contribution = top_10['Monetary'].sum() / rfm['Monetary'].sum()

    if contribution > 0.4:
        insights.append(f"Top 10 customers contribute {contribution:.2%} of revenue → high dependency risk.")
    else:
        insights.append(f"Revenue is well distributed (Top 10 contribute {contribution:.2%}).")

    # =========================
    # Loss-making products
    # =========================
    product_profit = df.groupby('Product Name')['Profit'].sum()
    loss_products = product_profit[product_profit < 0]

    if len(loss_products) > 0:
        insights.append(f"{len(loss_products)} products are loss-making, impacting profitability.")

    # =========================
    # Region performance
    # =========================
    region_perf = df.groupby('Region').agg({'Sales':'sum','Profit':'sum'})
    region_perf['Margin'] = region_perf['Profit'] / region_perf['Sales']

    best_region = region_perf['Margin'].idxmax()
    worst_region = region_perf['Margin'].idxmin()

    insights.append(f"{best_region} is most profitable region, while {worst_region} needs improvement.")

    # =========================
    # Discount impact
    # =========================
    corr = df[['Discount','Profit']].corr().iloc[0,1]

    if corr < -0.3:
        insights.append(f"High discounts significantly reduce profit (correlation: {corr:.2f}).")
    else:
        insights.append(f"Discount impact on profit is moderate (correlation: {corr:.2f}).")

    # =========================
    # Sales trend
    # =========================
    df['Month'] = df['Order Date'].dt.to_period('M').dt.to_timestamp()
    monthly_sales = df.groupby('Month')['Sales'].sum()

    growth = monthly_sales.pct_change().mean()

    if growth > 0:
        insights.append(f"Sales show an overall upward trend ({growth:.2%} avg growth).")
    else:
        insights.append(f"Sales trend is declining ({growth:.2%} avg growth).")

    # =========================
    # Sales forecast
    # =========================
        insights.append(f"Predicted next month sales: {prediction:.2f}")

    # Save
    with open(OUTPUT_DIR / "insights.txt", "w") as f:
        for i in insights:
            f.write("- " + i + "\n")

    return insights

def generate_recommendations(df, rfm):
    recommendations = []

    # =========================
    # Discount strategy
    # =========================
    corr = df[['Discount','Profit']].corr().iloc[0,1]

    if corr < -0.3:
        recommendations.append("Reduce high discount levels as they significantly impact profitability.")

    # =========================
    # Loss products
    # =========================
    loss_products = df.groupby('Product Name')['Profit'].sum()
    loss_products = loss_products[loss_products < 0]

    if len(loss_products) > 0:
        recommendations.append(f"Review pricing or discontinue {len(loss_products)} loss-making products.")

    # =========================
    # Customer strategy
    # =========================
    top_10 = rfm.sort_values(by='Monetary', ascending=False).head(10)
    contribution = top_10['Monetary'].sum() / rfm['Monetary'].sum()

    if contribution > 0.4:
        recommendations.append("Diversify customer base to reduce dependency on top customers.")
    else:
        recommendations.append("Strengthen loyalty programs to retain high-value customers.")

    # =========================
    # Regional strategy
    # =========================
    region_perf = df.groupby('Region').agg({'Sales':'sum','Profit':'sum'})
    region_perf['Margin'] = region_perf['Profit'] / region_perf['Sales']

    worst_region = region_perf['Margin'].idxmin()
    recommendations.append(f"Improve operations and pricing strategy in {worst_region} region.")

    # =========================
    # Growth strategy
    # =========================
    df['Month'] = df['Order Date'].dt.to_period('M').dt.to_timestamp()
    monthly_sales = df.groupby('Month')['Sales'].sum()

    growth = monthly_sales.pct_change().mean()

    if growth < 0:
        recommendations.append("Introduce marketing campaigns to boost declining sales.")
    else:
        recommendations.append("Capitalize on growth trend by increasing inventory and promotions.")

    # Save
    with open(OUTPUT_DIR / "recommendations.txt", "w") as f:
        for r in recommendations:
            f.write("- " + r + "\n")

    return recommendations