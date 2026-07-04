import requests
import streamlit as st
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_exchange_rate():
    """
    Fetch the latest USD to PLN exchange rate from a free API.
    Returns a float, or None if fails.
    """
    try:
        # Try exchangerate-api.com first
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        logger.info(f"Fetching exchange rate from: {url}")
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            rate = data.get('rates', {}).get('PLN')
            if rate:
                logger.info(f"✅ Exchange rate fetched: {rate}")
                return float(rate)
        logger.warning(f"⚠️ API returned status: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Error fetching exchange rate: {e}")
    
    # Fallback: try open.er-api.com
    try:
        url = "https://open.er-api.com/v6/latest/USD"
        logger.info(f"Fetching exchange rate from fallback: {url}")
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            rate = data.get('rates', {}).get('PLN')
            if rate:
                logger.info(f"✅ Exchange rate fetched (fallback): {rate}")
                return float(rate)
        logger.warning(f"⚠️ Fallback API returned status: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Error fetching exchange rate (fallback): {e}")
    
    return None

def get_current_rate():
    """
    Get the exchange rate from API.
    Caches it for 6 hours.
    Returns None if the API fails.
    """
    # Check if we have a valid rate in session state
    if 'exchange_rate' in st.session_state and 'rate_fetched_at' in st.session_state:
        elapsed = (datetime.now() - st.session_state.rate_fetched_at).total_seconds()
        if elapsed < 21600:  # 6 hours
            logger.info(f"📦 Using cached rate: {st.session_state.exchange_rate} (cached {elapsed/60:.1f} min ago)")
            return st.session_state.exchange_rate
    
    # Fetch fresh rate
    logger.info("🔄 Fetching fresh exchange rate...")
    rate = fetch_exchange_rate()
    
    # Store in session state
    st.session_state.exchange_rate = rate
    st.session_state.rate_fetched_at = datetime.now()
    
    if rate:
        logger.info(f"💾 Cached new rate: {rate}")
    else:
        logger.warning("⚠️ No rate available")
    
    return rate

def convert_pln_to_usd(amount_pln, rate=None):
    """Convert an amount in PLN to USD."""
    if rate is None:
        rate = get_current_rate()
    if rate is None or rate == 0:
        return None
    return amount_pln / rate

def convert_usd_to_pln(amount_usd, rate=None):
    """Convert an amount in USD to PLN."""
    if rate is None:
        rate = get_current_rate()
    if rate is None or rate == 0:
        return None
    return amount_usd * rate