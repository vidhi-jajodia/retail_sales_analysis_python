import matplotlib.pyplot as plt
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
SCREENSHOT_DIR = BASE_DIR / "screenshots"
SCREENSHOT_DIR.mkdir(exist_ok=True)

def save_plot(fig, filename: str):
    filepath = SCREENSHOT_DIR / filename
    fig.savefig(filepath)
    plt.close(fig)
    logger.info(f"Saved plot: {filepath}")