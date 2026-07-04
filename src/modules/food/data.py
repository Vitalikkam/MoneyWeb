"""
Food data layer – CRUD operations for food entries.
"""

from src.database import db
import pandas as pd
from datetime import datetime

def get_food_entries(date=None):
    """Get food entries. If date is provided, get entries for that date."""
    return db.get_food_entries(date)

def get_today_food_entries():
    """Get today's food entries."""
    today = datetime.today().strftime('%Y-%m-%d')
    return db.get_food_entries(today)

def add_food_entry(date, meal_type, food_name, calories, protein=0, carbs=0, fat=0,
                   vitamin_a=0, vitamin_c=0, vitamin_d=0, calcium=0, iron=0,
                   magnesium=0, zinc=0, potassium=0):
    """Add a new food entry with vitamins and minerals."""
    return db.add_food_entry(
        date, meal_type, food_name, calories, protein, carbs, fat,
        vitamin_a, vitamin_c, vitamin_d, calcium, iron, magnesium, zinc, potassium
    )

def delete_food_entry(entry_id):
    """Delete a food entry by ID."""
    try:
        conn = db._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM food_entries WHERE id = ?", (entry_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error deleting food entry: {e}")
        return False

def get_daily_summary(date=None):
    """Get daily nutrition summary including vitamins and minerals."""
    if date is None:
        date = datetime.today().strftime('%Y-%m-%d')
    
    entries = db.get_food_entries(date)
    if entries.empty:
        return {
            'total_calories': 0,
            'total_protein': 0,
            'total_carbs': 0,
            'total_fat': 0,
            'total_vitamin_a': 0,
            'total_vitamin_c': 0,
            'total_vitamin_d': 0,
            'total_calcium': 0,
            'total_iron': 0,
            'total_magnesium': 0,
            'total_zinc': 0,
            'total_potassium': 0,
            'meal_count': 0,
            'entries': []
        }
    
    return {
        'total_calories': entries['calories'].sum(),
        'total_protein': entries['protein'].sum(),
        'total_carbs': entries['carbs'].sum(),
        'total_fat': entries['fat'].sum(),
        'total_vitamin_a': entries.get('vitamin_a', 0).sum(),
        'total_vitamin_c': entries.get('vitamin_c', 0).sum(),
        'total_vitamin_d': entries.get('vitamin_d', 0).sum(),
        'total_calcium': entries.get('calcium', 0).sum(),
        'total_iron': entries.get('iron', 0).sum(),
        'total_magnesium': entries.get('magnesium', 0).sum(),
        'total_zinc': entries.get('zinc', 0).sum(),
        'total_potassium': entries.get('potassium', 0).sum(),
        'meal_count': len(entries),
        'entries': entries.to_dict('records')
    }