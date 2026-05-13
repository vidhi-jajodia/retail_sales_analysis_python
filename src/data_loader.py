from pathlib import Path
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def load_data(path: Path) -> pd.DataFrame:
    """Load dataset with error handling."""
    try:
        df = pd.read_csv(path, encoding='utf-8-sig')
        logger.info(f"Dataset loaded: {df.shape}")
        return df
    except FileNotFoundError:
        logger.error(f"File not found: {path}")
        raise