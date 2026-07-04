from supabase import create_client
import streamlit as st
import pandas as pd
from .interface import DatabaseInterface

class SupabaseClient(DatabaseInterface):
    """Supabase implementation for production."""
    
    def __init__(self):
        url = st.secrets["prod"]["SUPABASE_URL"]
        key = st.secrets["prod"]["SUPABASE_KEY"]
        self.supabase = create_client(url, key)
    
    # --- Transaction methods ---
    
    def get_transactions(self, start_date=None, end_date=None):
        try:
            query = self.supabase.table("transactions").select("*")
            if start_date and end_date:
                query = query.gte("Date", start_date).lte("Date", end_date)
            response = query.order("Date").execute()
            data = response.data
            if not data:
                return pd.DataFrame(columns=['id', 'Date', 'Deposit', 'Withdrawal'])
            df = pd.DataFrame(data)
            df['Date'] = pd.to_datetime(df['Date']).dt.date
            return df
        except Exception as e:
            st.error(f"Error fetching transactions: {e}")
            return pd.DataFrame(columns=['id', 'Date', 'Deposit', 'Withdrawal'])
    
    def add_transaction(self, date, deposit, withdrawal):
        try:
            self.supabase.table("transactions").insert({
                "Date": date,
                "Deposit": float(deposit),
                "Withdrawal": float(withdrawal)
            }).execute()
            return True
        except Exception as e:
            st.error(f"Error adding transaction: {e}")
            return False
    
    def update_transaction(self, id, date, deposit, withdrawal):
        try:
            self.supabase.table("transactions").update({
                "Date": date,
                "Deposit": float(deposit),
                "Withdrawal": float(withdrawal)
            }).eq("id", id).execute()
            return True
        except Exception as e:
            st.error(f"Error updating transaction: {e}")
            return False
    
    def delete_transaction(self, id):
        try:
            self.supabase.table("transactions").delete().eq("id", id).execute()
            return True
        except Exception as e:
            st.error(f"Error deleting transaction: {e}")
            return False
    
    # --- Food entry methods ---
    
    def get_food_entries(self, date=None):
        try:
            query = self.supabase.table("food_entries").select("*")
            if date:
                query = query.eq("Date", date)
            response = query.order("id", desc=True).execute()
            data = response.data
            if not data:
                return pd.DataFrame(columns=['id', 'Date', 'meal_type', 'food_name', 'calories', 'protein', 'carbs', 'fat'])
            df = pd.DataFrame(data)
            df['Date'] = pd.to_datetime(df['Date']).dt.date
            return df
        except Exception as e:
            st.error(f"Error fetching food entries: {e}")
            return pd.DataFrame(columns=['id', 'Date', 'meal_type', 'food_name', 'calories', 'protein', 'carbs', 'fat'])
    
    def add_food_entry(self, date, meal_type, food_name, calories, protein=0, carbs=0, fat=0,
                       vitamin_a=0, vitamin_c=0, vitamin_d=0, calcium=0, iron=0,
                       magnesium=0, zinc=0, potassium=0):
        """Add a food entry with vitamins and minerals to Supabase."""
        try:
            self.supabase.table("food_entries").insert({
                "Date": date,
                "meal_type": meal_type,
                "food_name": food_name,
                "calories": int(calories),
                "protein": float(protein),
                "carbs": float(carbs),
                "fat": float(fat),
                "vitamin_a": float(vitamin_a),
                "vitamin_c": float(vitamin_c),
                "vitamin_d": float(vitamin_d),
                "calcium": float(calcium),
                "iron": float(iron),
                "magnesium": float(magnesium),
                "zinc": float(zinc),
                "potassium": float(potassium)
            }).execute()
            return True
        except Exception as e:
            st.error(f"Error adding food entry: {e}")
            return False