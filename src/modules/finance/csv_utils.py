"""CSV import/export utilities for finance module."""

import pandas as pd
from src.database import db

def append_csv_data(uploaded_file):
    """
    Append data from a CSV file to the database.
    Returns (success, message, count).
    """
    try:
        df = pd.read_csv(uploaded_file)
        if df.empty:
            return False, "The CSV file is empty.", 0
        
        # Parse columns
        if 'Date' in df.columns and 'Deposit' in df.columns and 'Withdrawal' in df.columns:
            parsed_df = df[['Date', 'Deposit', 'Withdrawal']]
        else:
            return False, "CSV must have columns: Date, Deposit, Withdrawal", 0
        
        # Convert Date to ISO format
        parsed_df['Date'] = pd.to_datetime(parsed_df['Date']).dt.date
        
        # Add to database
        count = 0
        for _, row in parsed_df.iterrows():
            db.add_transaction(
                row['Date'],
                float(row['Deposit']),
                float(row['Withdrawal'])
            )
            count += 1
        
        return True, f"Successfully imported {count} transactions.", count
    except Exception as e:
        return False, f"Error importing CSV: {str(e)}", 0

def export_to_csv():
    """
    Export all transactions as a CSV string (for download).
    """
    df = db.get_transactions()
    if df.empty:
        return None
    
    df_export = df.drop(columns=['id'], errors='ignore')
    df_export['Date'] = df_export['Date'].astype(str)
    return df_export.to_csv(index=False).encode('utf-8')