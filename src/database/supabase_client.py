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

    def delete_food_entry(self, id):
        """Delete a food entry by ID."""
        try:
            self.supabase.table("food_entries").delete().eq("id", id).execute()
            return True
        except Exception as e:
            st.error(f"Error deleting food entry: {e}")
            return False

    # --- Supplements ---

    def get_supplements(self, start_date=None, end_date=None):
        """Get supplements for a date range."""
        try:
            query = self.supabase.table("supplements").select("*")
            if start_date and end_date:
                query = query.gte("Date", start_date).lte("Date", end_date)
            elif start_date:
                query = query.eq("Date", start_date)
            response = query.execute()
            data = response.data
            if not data:
                return pd.DataFrame(columns=['id', 'Date', 'supplement_name', 'dosage', 'unit', 'taken'])
            return pd.DataFrame(data)
        except Exception as e:
            st.error(f"Error fetching supplements: {e}")
            return pd.DataFrame(columns=['id', 'Date', 'supplement_name', 'dosage', 'unit', 'taken'])

    def set_supplement_taken(self, date, supplement_name, dosage, unit, taken):
        """Insert or update supplement taken status."""
        try:
            # Check if row exists
            response = self.supabase.table("supplements") \
                .select("id") \
                .eq("Date", date) \
                .eq("supplement_name", supplement_name) \
                .execute()
            if response.data:
                self.supabase.table("supplements").update({
                    "taken": taken, "dosage": float(dosage), "unit": unit
                }).eq("Date", date).eq("supplement_name", supplement_name).execute()
            else:
                self.supabase.table("supplements").insert({
                    "Date": date,
                    "supplement_name": supplement_name,
                    "dosage": float(dosage),
                    "unit": unit,
                    "taken": taken
                }).execute()
            return True
        except Exception as e:
            st.error(f"Error setting supplement: {e}")
            return False

    def delete_supplement(self, id):
        """Delete a supplement entry by ID."""
        try:
            self.supabase.table("supplements").delete().eq("id", id).execute()
            return True
        except Exception as e:
            st.error(f"Error deleting supplement: {e}")
            return False

    # --- Vocabulary ---

    def get_vocabulary(self):
        """Get all vocabulary words."""
        try:
            response = self.supabase.table("vocabulary").select("*").order("word").execute()
            data = response.data
            if not data:
                return pd.DataFrame()
            return pd.DataFrame(data)
        except Exception as e:
            st.error(f"Error fetching vocabulary: {e}")
            return pd.DataFrame()

    def add_vocabulary(self, word, cefr_level, definition, example,
                       translation=None, importance=3, category='general', mastery=4):
        """Add a new vocabulary word."""
        from datetime import datetime, timedelta
        today = datetime.today().strftime('%Y-%m-%d')
        next_review = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')
        try:
            self.supabase.table("vocabulary").insert({
                "word": word,
                "cefr_level": cefr_level,
                "definition": definition,
                "example_sentence": example,
                "translation": translation,
                "importance": importance,
                "category": category,
                "mastery": mastery,
                "date_added": today,
                "last_reviewed": today,
                "next_review_date": next_review,
                "times_reviewed": 0
            }).execute()
            return True
        except Exception as e:
            st.error(f"Error adding vocabulary: {e}")
            return False

    def update_vocabulary_review(self, word, mastery, next_review_date):
        """Update review status for a word."""
        from datetime import datetime
        today = datetime.today().strftime('%Y-%m-%d')
        try:
            self.supabase.table("vocabulary").update({
                "mastery": mastery,
                "last_reviewed": today,
                "next_review_date": next_review_date,
                "times_reviewed": self._increment_times_reviewed(word)
            }).eq("word", word).execute()
            return True
        except Exception as e:
            st.error(f"Error updating vocabulary review: {e}")
            return False

    def _increment_times_reviewed(self, word):
        """Get current times_reviewed + 1 for a word."""
        try:
            response = self.supabase.table("vocabulary") \
                .select("times_reviewed").eq("word", word).execute()
            if response.data:
                return (response.data[0].get("times_reviewed") or 0) + 1
        except Exception:
            pass
        return 1

    def delete_vocabulary(self, word):
        """Delete a vocabulary word."""
        try:
            self.supabase.table("vocabulary").delete().eq("word", word).execute()
            return True
        except Exception as e:
            st.error(f"Error deleting vocabulary: {e}")
            return False

    def word_exists(self, word):
        """Check if a word already exists."""
        try:
            response = self.supabase.table("vocabulary") \
                .select("id").eq("word", word).execute()
            return len(response.data) > 0
        except Exception:
            return False

    def get_vocabulary_due(self, date):
        """Get vocabulary words due for review on or before a date."""
        try:
            response = self.supabase.table("vocabulary") \
                .select("*").lte("next_review_date", date) \
                .order("next_review_date").execute()
            data = response.data
            if not data:
                return pd.DataFrame()
            return pd.DataFrame(data)
        except Exception as e:
            st.error(f"Error fetching due vocabulary: {e}")
            return pd.DataFrame()