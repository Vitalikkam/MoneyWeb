from src.database import db
import pandas as pd

def get_all_transactions():
    """Get all transactions from the database."""
    return db.get_transactions()

def add_transaction(date, deposit, withdrawal):
    """Add a new transaction."""
    return db.add_transaction(date, deposit, withdrawal)

def save_dataframe(df):
    """
    Save a dataframe of transactions.
    Handles both dataframes with and without 'id' column.
    """
    # If df has no 'id' column, treat all rows as new
    if 'id' not in df.columns:
        # Check for duplicates before adding
        existing = db.get_transactions()
        
        # Create a set of existing (Date, Deposit, Withdrawal) tuples
        existing_set = set()
        if not existing.empty:
            for _, row in existing.iterrows():
                existing_set.add((row['Date'], float(row['Deposit']), float(row['Withdrawal'])))
        
        # Only add rows that don't already exist
        added = 0
        for _, row in df.iterrows():
            key = (row['Date'], float(row['Deposit']), float(row['Withdrawal']))
            if key not in existing_set:
                db.add_transaction(
                    row['Date'],
                    float(row['Deposit']),
                    float(row['Withdrawal'])
                )
                added += 1
        
        if added > 0:
            print(f"Added {added} new transactions")
        return True
    
    # If df has 'id' column, update existing and add new
    existing = db.get_transactions()
    existing_ids = set(existing['id'].tolist()) if not existing.empty else set()
    new_ids = set(df['id'].tolist()) if not df.empty else set()
    
    # Find deleted rows (in existing but not in new)
    deleted_ids = existing_ids - new_ids
    for tx_id in deleted_ids:
        db.delete_transaction(tx_id)
    
    # Update or insert each row
    for _, row in df.iterrows():
        if row['id'] in existing_ids:
            # Update existing
            db.update_transaction(
                row['id'],
                row['Date'],
                float(row['Deposit']),
                float(row['Withdrawal'])
            )
        else:
            # Insert new
            db.add_transaction(
                row['Date'],
                float(row['Deposit']),
                float(row['Withdrawal'])
            )
    return True

def delete_transaction(tx_id):
    return db.delete_transaction(tx_id)

def get_summary():
    df = db.get_transactions()
    if df.empty:
        return {"total_deposits": 0, "total_withdrawals": 0, "total_balance": 0}
    return {
        "total_deposits": df['Deposit'].sum(),
        "total_withdrawals": df['Withdrawal'].sum(),
        "total_balance": df['Deposit'].sum() - df['Withdrawal'].sum()
    }

def clear_all_data():
    """Clear all transactions."""
    df = db.get_transactions()
    if df.empty:
        return True
    for _, row in df.iterrows():
        db.delete_transaction(row['id'])
    return True