
import pandas as pd
import json

def read_csv(file):
    """
    Reads a CSV file and returns a pandas DataFrame.
    Handles common data quality issues during import.
    """
    # Read CSV with flexible parsing - keep all columns as strings initially
    df = pd.read_csv(
        file,
        na_values=['', ' ', 'NA', 'N/A', 'null', 'NULL', 'None'],
        keep_default_na=True,
        dtype=str,  # Read everything as string to prevent auto-conversion issues
        low_memory=False
    )

    # Drop completely empty columns
    df = df.dropna(axis=1, how='all')

    # Remove unnamed columns (artifacts from Excel)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False)]

    # Clean up whitespace in string columns
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].str.strip() if df[col].notna().any() else df[col]

    return df

def read_json(file):
    """Reads a JSON file and returns a dictionary."""
    return json.load(file)
