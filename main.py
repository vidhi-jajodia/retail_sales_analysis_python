import logging
from src.analysis import run_analysis

def main():
    logging.basicConfig(level=logging.INFO)

    logging.info("Starting pipeline...")
    run_analysis()
    logging.info("Analysis complete.")

if __name__ == "__main__":
    main()