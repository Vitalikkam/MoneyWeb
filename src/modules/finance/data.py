from src.database import db
import pandas as pd

def _normalize_columns(df):
    """Rename columns to match expected format (Deposit, Withdrawal)."""
    if df.empty:
        return df
    # Rename lowercase columns to capitalized
    rename_map = {}
    for col in df.columns:
        if col.lower() == 'deposit' and col != 'Deposit':
            rename_map[col] = 'Deposit'
        elif col.lower() == 'withdrawal' and col != 'Withdrawal':
            rename_map[col] = 'Withdrawal'
    if rename_map:
        df = df.rename(columns=rename_map)
    return df

def get_all_transactions():
    """Get all transactions from the database."""
    df = db.get_transactions()
    return _normalize_columns(df)

def add_transaction(date, deposit, withdrawal):
    """Add a new transaction."""
    return db.add_transaction(date, deposit, withdrawal)

def save_dataframe(df):
    """Save a dataframe of transactions."""
    # Ensure columns are normalized
    df = _normalize_columns(df)
    
    if 'id' not in df.columns:
        for _, row in df.iterrows():
            db.add_transaction(
                row['Date'],
                float(row['Deposit']),
                float(row['Withdrawal'])
            )
        return True
    
    existing = db.get_transactions()
    existing = _normalize_columns(existing)
    existing_ids = set(existing['id'].tolist()) if not existing.empty else set()
    new_ids = set(df['id'].tolist()) if not df.empty else set()
    
    deleted_ids = existing_ids - new_ids
    for tx_id in deleted_ids:
        db.delete_transaction(tx_id)
    
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
    df = _normalize_columns(df)
    if df.empty:
        return {"total_deposits": 0, "total_withdrawals": 0, "total_balance": 0}
    total_deposits = df['Deposit'].sum()
    total_withdrawals = df['Withdrawal'].sum()
    total_balance = total_deposits - total_withdrawals
    return {
        "total_deposits": total_deposits,
        "total_withdrawals": total_withdrawals,
        "total_balance": total_balance
    }

