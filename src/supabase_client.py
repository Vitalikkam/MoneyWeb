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
        # Convert date column
        df['date'] = pd.to_datetime(df['date']).dt.date
        # Rename columns to match app expectations
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