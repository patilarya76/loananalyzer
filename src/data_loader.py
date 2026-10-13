"""
data_loader.py
--------------
Responsible for Feature 2: Data Ingestion.

Functions in this module:
1. load_loan_data(filepath): Reads CSV file using pandas, performs initial checks,
   displays summary information, and returns a DataFrame.
"""

import os
import pandas as pd


def load_loan_data(filepath: str) -> pd.DataFrame:
    """
    Load loan repayment records from a CSV file into a pandas DataFrame.

    Parameters:
    -----------
    filepath : str
        Relative or absolute path to the CSV file.

    Returns:
    --------
    pd.DataFrame
        DataFrame containing raw loan repayment records.

    Raises:
    -------
    FileNotFoundError: If the specified file does not exist.
    ValueError: If the file is empty or cannot be parsed as a CSV.
    """
    # Check if the file exists on the filesystem
    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"Error: The dataset file '{filepath}' was not found. "
            "Please ensure the file exists in the specified directory."
        )

    try:
        # Load CSV using pandas
        # We specify keep_default_na=True so empty cells are treated as NaN
        df = pd.read_csv(filepath)
    except pd.errors.EmptyDataError:
        raise ValueError(f"Error: The file '{filepath}' is empty.")
    except Exception as exc:
        raise ValueError(f"Error reading '{filepath}': {exc}")

    # Display dataset metadata for user and interview walkthrough
    print("=" * 70)
    print("  DATA INGESTION SUMMARY")
    print("=" * 70)
    print(f"Dataset Path        : {filepath}")
    print(f"Total Records (Rows): {df.shape[0]}")
    print(f"Total Columns       : {df.shape[1]}")
    print("\nColumns and Data Types:")
    for col, dtype in df.dtypes.items():
        print(f"  - {col:<20} : {dtype}")

    print("\nFirst 5 Records Preview:")
    print("-" * 70)
    print(df.head(5).to_string(index=False))
    print("=" * 70)

    return df


if __name__ == "__main__":
    # Test script standalone
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "loan_data.csv")
    loaded_df = load_loan_data(data_path)
    print(f"\n[Test] Loaded {len(loaded_df)} records successfully.")
