import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from pathlib import Path
import matplotlib.pyplot as plt

from src.visualization import save_plot

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "outputs"


def create_features(df):
    """Create time-series features"""

    df = df.copy()

    # Lag features
    df['lag_1'] = df['Sales'].shift(1)
    df['lag_2'] = df['Sales'].shift(2)
    df['lag_3'] = df['Sales'].shift(3)

    # Rolling mean
    df['rolling_mean_3'] = df['Sales'].rolling(window=3).mean()

    # Trend
    df['t'] = np.arange(len(df))

    # Month (seasonality)
    df['month'] = df['Month'].dt.month

    df = df.dropna()

    return df


def forecast_sales(df):
    """Improved forecasting with feature engineering"""

    # Prepare data
    df['Month'] = df['Order Date'].dt.to_period('M').dt.to_timestamp()
    monthly = df.groupby('Month')['Sales'].sum().reset_index()

    # Feature engineering
    feature_df = create_features(monthly)

    X = feature_df[['lag_1','lag_2','lag_3','rolling_mean_3','t','month']]
    y = feature_df['Sales']

    model = LinearRegression()
    model.fit(X, y)

    # =========================
    # Model : MAE mean_absolute_error
    # =========================
    y_pred = model.predict(X)
    mae = mean_absolute_error(y, y_pred)

    print(f"📊 Model MAE: {mae:.2f}")

    # Prepare next month input
    last_row = feature_df.iloc[-1]

    next_features = pd.DataFrame({
        'lag_1': [last_row['Sales']],
        'lag_2': [last_row['lag_1']],
        'lag_3': [last_row['lag_2']],
        'rolling_mean_3': [(last_row['Sales'] + last_row['lag_1'] + last_row['lag_2']) / 3],
        't': [last_row['t'] + 1],
        'month': [(last_row['month'] % 12) + 1]
    })

    prediction = model.predict(next_features)[0]

    # Save output
    pd.DataFrame({
        "Next_Month_Predicted_Sales": [prediction]
    }).to_csv(OUTPUT_DIR / "sales_forecast.csv", index=False)

    # Plot
    fig, ax = plt.subplots()
    ax.plot(monthly['Month'], monthly['Sales'], label="Actual")

    next_month = monthly['Month'].max() + pd.DateOffset(months=1)
    ax.scatter(next_month, prediction, color='red', label="Forecast")

    ax.set_title("Sales Forecast")
    ax.legend()

    save_plot(fig, "sales_forecast.png")

    return prediction