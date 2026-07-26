from src.database import db
import pandas as pd

def get_all_transactions():
    """Get all transactions from the database."""
    df = db.get_transactions()
    # The database already returns columns with proper names from supabase_client
    return df

def add_transaction(date, deposit, withdrawal):
    """Add a new transaction."""
    return db.add_transaction(date, deposit, withdrawal)

def save_dataframe(df):
    """Save a dataframe of transactions."""
    # If df has no 'id' column, treat all rows as new
    if 'id' not in df.columns:
        for _, row in df.iterrows():
            db.add_transaction(
                row['Date'],
                float(row['Deposit']),
                float(row['Withdrawal'])
            )
        return True
    
    # If df has 'id' column, update existing and add new
    existing = db.get_transactions()
    existing_ids = set(existing['id'].tolist()) if not existing.empty else set()
    new_ids = set(df['id'].tolist()) if not df.empty else set()
    
    # Find deleted rows
    deleted_ids = existing_ids - new_ids
    for tx_id in deleted_ids:
        db.delete_transaction(tx_id)
    
    # Update or insert each row
    for _, row in df.iterrows():
        if row['id'] in existing_ids:
            db.update_transaction(
                row['id'],
                row['Date'],
                float(row['Deposit']),
                float(row['Withdrawal'])
            )
        else:
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
    # Use lowercase column names from Supabase
    deposit_col = 'Deposit' if 'Deposit' in df.columns else 'deposit'
    withdrawal_col = 'Withdrawal' if 'Withdrawal' in df.columns else 'withdrawal'
    
    total_deposits = df[deposit_col].sum()
    total_withdrawals = df[withdrawal_col].sum()
    total_balance = total_deposits - total_withdrawals
    return {
        "total_deposits": total_deposits,
        "total_withdrawals": total_withdrawals,
        "total_balance": total_balance
    }

