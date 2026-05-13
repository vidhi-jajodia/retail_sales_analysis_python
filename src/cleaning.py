import pandas as pd
import logging

logger = logging.getLogger(__name__)

def clean_numeric_column(df: pd.DataFrame, col: str) -> pd.DataFrame:
    df[col] = (
        df[col]
        .astype(str)
        .str.replace(',', '', regex=False)
        .pipe(pd.to_numeric, errors='coerce')
    )
    return df

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean dataset."""
    
    df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True)
    df = df.drop_duplicates()

    numeric_cols = ['Sales', 'Profit', 'Discount', 'Shipping Cost']
    for col in numeric_cols:
        df = clean_numeric_column(df, col)

    logger.info(f"Cleaned data shape: {df.shape}")
    return df