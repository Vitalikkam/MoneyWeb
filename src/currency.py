import requests
import streamlit as st
from datetime import datetime

def fetch_exchange_rate():
    """
    Fetch the latest USD to PLN exchange rate from a free API (no key required).
    Returns a float, or None if fails.
    """
    try:
        # Using exchangerate-api.com (free, no key)
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            rate = data.get('rates', {}).get('PLN')
            if rate:
                return float(rate)
    except Exception as e:
        print(f"Error fetching exchange rate: {e}")
    
    # Fallback try: another free API
    try:
        url = "https://open.er-api.com/v6/latest/USD"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            rate = data.get('rates', {}).get('PLN')
            if rate:
                return float(rate)
    except Exception as e:
        print(f"Error fetching exchange rate (fallback): {e}")
    
    return None

def get_current_rate():
    """
    Get the exchange rate from API.
    Caches it for 6 hours.
    Returns None if the API fails (NO FALLBACK).
    """
    # Check if we have a valid rate in session state (fetched within last 6 hours)
    if 'exchange_rate' in st.session_state and 'rate_fetched_at' in st.session_state:
        elapsed = (datetime.now() - st.session_state.rate_fetched_at).total_seconds()
        if elapsed < 21600:  # 6 hours
            return st.session_state.exchange_rate
    
    # Fetch fresh rate
    rate = fetch_exchange_rate()
    
    # Store in session state (even if None, so we don't spam the API)
    st.session_state.exchange_rate = rate
    st.session_state.rate_fetched_at = datetime.now()
    
    return rate

def convert_pln_to_usd(amount_pln, rate=None):
    """Convert an amount in PLN to USD using the given rate."""
    if rate is None:
        rate = get_current_rate()
    if rate is None or rate == 0:
        return None
    return amount_pln / rate

def convert_usd_to_pln(amount_usd, rate=None):
    """Convert an amount in USD to PLN using the given rate."""
    if rate is None:
        rate = get_current_rate()
    if rate is None or rate == 0:
        return None
    return amount_usd * rate