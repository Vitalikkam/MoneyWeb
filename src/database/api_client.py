"""
API Client for the remote finance database.
Connects to your Mac's API server via ngrok/Cloudflare.
"""

import requests
import streamlit as st
import pandas as pd
from datetime import datetime

def get_api_url():
    """Get the API URL from secrets."""
    return st.secrets["API_URL"]

def get_all_transactions():
    """Fetch all transactions from the remote API."""
    try:
        url = f"{get_api_url()}/api/transactions"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if not data:
            return pd.DataFrame(columns=['id', 'Date', 'Deposit', 'Withdrawal'])
        df = pd.DataFrame(data)
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        return df
    except Exception as e:
        st.error(f"⚠️ Error connecting to your Mac: {str(e)}")
        st.info("💡 Make sure your Mac is on, the API server is running, and ngrok is active.")
        return pd.DataFrame(columns=['id', 'Date', 'Deposit', 'Withdrawal'])

def add_transaction(date, deposit, withdrawal):
    """Add a new transaction via the remote API."""
    try:
        url = f"{get_api_url()}/api/transactions"
        payload = {
            "Date": date.isoformat(),
            "Deposit": float(deposit),
            "Withdrawal": float(withdrawal)
        }
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        st.error(f"⚠️ Error adding transaction: {str(e)}")
        return False

def save_dataframe(df):
    """Save all transactions via the remote API (updates and deletes)."""
    # First, get all existing IDs
    existing = get_all_transactions()
    existing_ids = set(existing['id'].tolist()) if not existing.empty else set()
    new_ids = set(df['id'].tolist()) if not df.empty else set()
    
    # Find deleted rows (in existing but not in new)
    deleted_ids = existing_ids - new_ids
    for tx_id in deleted_ids:
        try:
            url = f"{get_api_url()}/api/transactions/{tx_id}"
            response = requests.delete(url, timeout=10)
            response.raise_for_status()
        except Exception as e:
            st.error(f"⚠️ Error deleting transaction {tx_id}: {str(e)}")
            return False
    
    # Update or insert each row
    for _, row in df.iterrows():
        try:
            if row['id'] in existing_ids:
                # Update existing
                url = f"{get_api_url()}/api/transactions/{row['id']}"
                payload = {
                    "Date": row['Date'].isoformat() if hasattr(row['Date'], 'isoformat') else str(row['Date']),
                    "Deposit": float(row['Deposit']),
                    "Withdrawal": float(row['Withdrawal'])
                }
                response = requests.put(url, json=payload, timeout=10)
            else:
                # Insert new
                url = f"{get_api_url()}/api/transactions"
                payload = {
                    "Date": row['Date'].isoformat() if hasattr(row['Date'], 'isoformat') else str(row['Date']),
                    "Deposit": float(row['Deposit']),
                    "Withdrawal": float(row['Withdrawal'])
                }
                response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
        except Exception as e:
            st.error(f"⚠️ Error saving transaction: {str(e)}")
            return False
    return True

def get_summary():
    """Get summary statistics from the remote API."""
    try:
        url = f"{get_api_url()}/api/summary"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"⚠️ Error getting summary: {str(e)}")
        return {"total_deposits": 0, "total_withdrawals": 0, "total_balance": 0}