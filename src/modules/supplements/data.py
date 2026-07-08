"""
Supplements data layer – CRUD operations for supplement entries.
"""

from src.database import db
import pandas as pd
from datetime import datetime
from .config import DEFAULT_SUPPLEMENTS

def get_supplements(start_date=None, end_date=None):
    """Get supplements for a date range."""
    return db.get_supplements(start_date, end_date)

def get_supplements_for_month(year, month):
    """Get all supplements for a specific month."""
    start_date = f"{year}-{month:02d}-01"
    # Get last day of month
    import calendar
    last_day = calendar.monthrange(year, month)[1]
    end_date = f"{year}-{month:02d}-{last_day:02d}"
    return db.get_supplements(start_date, end_date)

def get_supplements_for_date(date):
    """Get supplements for a specific date."""
    return db.get_supplements(date)

def set_supplement_taken(date, supplement_name, dosage, unit, taken):
    """Set supplement taken status."""
    return db.set_supplement_taken(date, supplement_name, dosage, unit, taken)

def add_supplement(date, supplement_name, dosage, unit):
    """Add a new supplement entry."""
    return db.add_supplement(date, supplement_name, dosage, unit)

def delete_supplement(entry_id):
    """Delete a supplement entry by ID."""
    return db.delete_supplement(entry_id)

def get_daily_summary(date):
    """Get summary for a specific date."""
    df = db.get_supplements(date)
    if df.empty:
        return {
            'total': 0,
            'taken': 0,
            'percentage': 0,
            'entries': []
        }
    
    total = len(DEFAULT_SUPPLEMENTS)
    taken = df[df['taken'] == 1].shape[0] if not df.empty else 0
    
    return {
        'total': total,
        'taken': taken,
        'percentage': (taken / total * 100) if total > 0 else 0,
        'entries': df.to_dict('records')
    }

def get_weekly_summary(year, month):
    """Get weekly summary for a month."""
    df = get_supplements_for_month(year, month)
    if df.empty:
        return {}
    
    # Group by date and count taken
    df['taken'] = df['taken'].astype(int)
    summary = df.groupby('Date')['taken'].sum().to_dict()
    return summary