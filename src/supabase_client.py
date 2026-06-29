import streamlit as st
import pandas as pd
from supabase import create_client

def get_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

def get_all_transactions():
    try:
        supabase = get_supabase()
        response = supabase.table("transactions").select("*").order("date").execute()
        data = response.data
        if not data:
            return pd.DataFrame(columns=['id', 'Date', 'Deposit', 'Withdrawal'])
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date']).dt.date
        df.rename(columns={
            'date': 'Date',
            'deposit': 'Deposit',
            'withdrawal': 'Withdrawal'
        }, inplace=True)
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame(columns=['id', 'Date', 'Deposit', 'Withdrawal'])

def add_transaction(date_obj, deposit, withdrawal):
    try:
        supabase = get_supabase()
        supabase.table("transactions").insert({
            "date": date_obj.isoformat(),
            "deposit": float(deposit),
            "withdrawal": float(withdrawal)
        }).execute()
        return True
    except Exception as e:
        st.error(f"Error adding transaction: {e}")
        return False

def save_dataframe(df):
    try:
        supabase = get_supabase()
        for _, row in df.iterrows():
            date_str = row['Date'].isoformat() if hasattr(row['Date'], 'isoformat') else str(row['Date'])
            supabase.table("transactions").upsert({
                "id": int(row['id']),
                "date": date_str,
                "deposit": float(row['Deposit']),
                "withdrawal": float(row['Withdrawal'])
            }).execute()
        return True
    except Exception as e:
        st.error(f"Error saving transactions: {e}")
        return False

def delete_transaction(tx_id):
    try:
        supabase = get_supabase()
        supabase.table("transactions").delete().eq("id", tx_id).execute()
        return True
    except Exception as e:
        st.error(f"Error deleting transaction: {e}")
        return False

def get_summary():
    try:
        supabase = get_supabase()
        response = supabase.table("transactions").select("*").execute()
        data = response.data
        if not data:
            return {"total_deposits": 0, "total_withdrawals": 0, "total_balance": 0}
        df = pd.DataFrame(data)
        total_deposits = df['deposit'].sum()
        total_withdrawals = df['withdrawal'].sum()
        total_balance = total_deposits - total_withdrawals
        return {
            "total_deposits": total_deposits,
            "total_withdrawals": total_withdrawals,
            "total_balance": total_balance
        }
    except Exception as e:
        st.error(f"Error getting summary: {e}")
        return {"total_deposits": 0, "total_withdrawals": 0, "total_balance": 0}

# ---------- CSV Functions ----------
def append_csv_data(uploaded_file):
    """
    Append data from a CSV file to Supabase.
    Returns (success, message, count).
    """
    try:
        df = pd.read_csv(uploaded_file)
        if df.empty:
            return False, "The CSV file is empty.", 0
        
        # Parse columns (simple version – assumes Date, Deposit, Withdrawal)
        # Or try to detect columns
        if 'Date' in df.columns and 'Deposit' in df.columns and 'Withdrawal' in df.columns:
            parsed_df = df[['Date', 'Deposit', 'Withdrawal']]
        elif 'date' in df.columns and 'deposit' in df.columns and 'withdrawal' in df.columns:
            parsed_df = df[['date', 'deposit', 'withdrawal']]
            parsed_df.rename(columns={
                'date': 'Date',
                'deposit': 'Deposit',
                'withdrawal': 'Withdrawal'
            }, inplace=True)
        else:
            return False, "CSV must have columns: Date, Deposit, Withdrawal", 0
        
        # Convert Date to ISO format
        parsed_df['Date'] = pd.to_datetime(parsed_df['Date']).dt.date
        
        # Upload to Supabase
        supabase = get_supabase()
        for _, row in parsed_df.iterrows():
            supabase.table("transactions").insert({
                "date": row['Date'].isoformat(),
                "deposit": float(row['Deposit']),
                "withdrawal": float(row['Withdrawal'])
            }).execute()
        
        return True, f"Successfully imported {len(parsed_df)} transactions.", len(parsed_df)
    except Exception as e:
        return False, f"Error importing CSV: {str(e)}", 0

def export_to_csv():
    """
    Export all transactions as a CSV string (for download).
    """
    df = get_all_transactions()
    if df.empty:
        return None
    
    df_export = df.drop(columns=['id'], errors='ignore')
    df_export['Date'] = df_export['Date'].astype(str)
    return df_export.to_csv(index=False).encode('utf-8')

def clear_all_data():
    """
    Delete ALL transactions from Supabase.
    """
    try:
        supabase = get_supabase()
        supabase.table("transactions").delete().neq("id", 0).execute()
        return True
    except Exception as e:
        st.error(f"Error clearing data: {e}")
        return False