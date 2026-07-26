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
    
    # ============================================
    # TRANSACTION METHODS
    # ============================================
    
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
    
    # ============================================
    # FOOD ENTRY METHODS
    # ============================================
    
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
    
    # ============================================
    # SUPPLEMENT METHODS
    # ============================================
    
    def get_supplements(self, start_date=None, end_date=None):
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
            df = pd.DataFrame(data)
            df['Date'] = pd.to_datetime(df['Date']).dt.date
            return df
        except Exception as e:
            st.error(f"Error fetching supplements: {e}")
            return pd.DataFrame(columns=['id', 'Date', 'supplement_name', 'dosage', 'unit', 'taken'])
    
    def add_supplement(self, date, supplement_name, dosage, unit):
        try:
            self.supabase.table("supplements").insert({
                "Date": date,
                "supplement_name": supplement_name,
                "dosage": float(dosage),
                "unit": unit
            }).execute()
            return True
        except Exception as e:
            st.error(f"Error adding supplement: {e}")
            return False
    
    def set_supplement_taken(self, date, supplement_name, dosage, unit, taken):
        try:
            # Check if entry exists
            response = self.supabase.table("supplements").select("id").eq("Date", date).eq("supplement_name", supplement_name).execute()
            
            if response.data:
                # Update existing
                self.supabase.table("supplements").update({
                    "taken": taken,
                    "dosage": float(dosage),
                    "unit": unit
                }).eq("Date", date).eq("supplement_name", supplement_name).execute()
            else:
                # Insert new
                self.supabase.table("supplements").insert({
                    "Date": date,
                    "supplement_name": supplement_name,
                    "dosage": float(dosage),
                    "unit": unit,
                    "taken": taken
                }).execute()
            return True
        except Exception as e:
            st.error(f"Error updating supplement: {e}")
            return False
    
    def delete_supplement(self, id):
        try:
            self.supabase.table("supplements").delete().eq("id", id).execute()
            return True
        except Exception as e:
            st.error(f"Error deleting supplement: {e}")
            return False
    
    # ============================================
    # VOCABULARY METHODS
    # ============================================
    
    def get_vocabulary(self, word=None):
        try:
            query = self.supabase.table("vocabulary").select("*")
            if word:
                query = query.eq("word", word)
            response = query.order("word").execute()
            data = response.data
            if not data:
                return pd.DataFrame(columns=['id', 'word', 'cefr_level', 'definition', 'example_sentence', 'translation', 'importance', 'mastery', 'category', 'date_added', 'last_reviewed', 'times_reviewed', 'next_review_date'])
            df = pd.DataFrame(data)
            df['date_added'] = pd.to_datetime(df['date_added']).dt.date if 'date_added' in df.columns else None
            df['last_reviewed'] = pd.to_datetime(df['last_reviewed']).dt.date if 'last_reviewed' in df.columns else None
            df['next_review_date'] = pd.to_datetime(df['next_review_date']).dt.date if 'next_review_date' in df.columns else None
            return df
        except Exception as e:
            st.error(f"Error fetching vocabulary: {e}")
            return pd.DataFrame(columns=['id', 'word', 'cefr_level', 'definition', 'example_sentence', 'translation', 'importance', 'mastery', 'category', 'date_added', 'last_reviewed', 'times_reviewed', 'next_review_date'])
    
    def add_vocabulary(self, word, cefr_level, definition, example_sentence, translation=None,
                       importance=3, category="general", mastery=4, date_added=None, last_reviewed=None, next_review_date=None):
        try:
            import datetime
            today = datetime.datetime.today().strftime('%Y-%m-%d')
            if not date_added:
                date_added = today
            if not last_reviewed:
                last_reviewed = today
            if not next_review_date:
                next_review_date = (datetime.datetime.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
            
            self.supabase.table("vocabulary").insert({
                "word": word,
                "cefr_level": cefr_level,
                "definition": definition,
                "example_sentence": example_sentence,
                "translation": translation,
                "importance": importance,
                "category": category,
                "mastery": mastery,
                "date_added": date_added,
                "last_reviewed": last_reviewed,
                "next_review_date": next_review_date
            }).execute()
            return True
        except Exception as e:
            st.error(f"Error adding vocabulary: {e}")
            return False
    
    def update_vocabulary_review(self, word, mastery):
        try:
            import datetime
            today = datetime.datetime.today().strftime('%Y-%m-%d')
            if mastery <= 2:
                days_to_add = 30
            elif mastery == 3:
                days_to_add = 14
            elif mastery == 4:
                days_to_add = 7
            else:
                days_to_add = 3
            next_review = (datetime.datetime.today() + datetime.timedelta(days=days_to_add)).strftime('%Y-%m-%d')
            
            self.supabase.table("vocabulary").update({
                "mastery": mastery,
                "last_reviewed": today,
                "next_review_date": next_review,
                "times_reviewed": self.supabase.table("vocabulary").select("times_reviewed").eq("word", word).execute().data[0]['times_reviewed'] + 1
            }).eq("word", word).execute()
            return True
        except Exception as e:
            st.error(f"Error updating vocabulary review: {e}")
            return False
    
    def delete_vocabulary(self, word):
        try:
            self.supabase.table("vocabulary").delete().eq("word", word).execute()
            return True
        except Exception as e:
            st.error(f"Error deleting vocabulary: {e}")
            return False
    
    # ============================================
    # LEARNING METHODS
    # ============================================
    
    def get_learning_subjects(self, status=None):
        try:
            query = self.supabase.table("learning_subjects").select("*")
            if status:
                query = query.eq("status", status)
            response = query.order("name").execute()
            data = response.data
            if not data:
                return pd.DataFrame(columns=['id', 'name', 'category', 'priority', 'goal', 'status', 'start_date', 'target_date', 'completion_percentage', 'created_at'])
            df = pd.DataFrame(data)
            df['start_date'] = pd.to_datetime(df['start_date']).dt.date if 'start_date' in df.columns else None
            df['target_date'] = pd.to_datetime(df['target_date']).dt.date if 'target_date' in df.columns else None
            return df
        except Exception as e:
            st.error(f"Error fetching learning subjects: {e}")
            return pd.DataFrame(columns=['id', 'name', 'category', 'priority', 'goal', 'status', 'start_date', 'target_date', 'completion_percentage', 'created_at'])
    
    def add_learning_subject(self, name, category, priority, goal, status, start_date, target_date):
        try:
            response = self.supabase.table("learning_subjects").insert({
                "name": name,
                "category": category,
                "priority": priority,
                "goal": goal,
                "status": status,
                "start_date": start_date,
                "target_date": target_date
            }).execute()
            return response.data[0]['id'] if response.data else None
        except Exception as e:
            st.error(f"Error adding learning subject: {e}")
            return None
    
    def update_learning_subject_status(self, subject_id, status):
        try:
            self.supabase.table("learning_subjects").update({"status": status}).eq("id", subject_id).execute()
            return True
        except Exception as e:
            st.error(f"Error updating learning subject status: {e}")
            return False
    
    def update_learning_subject_progress(self, subject_id, percentage):
        try:
            self.supabase.table("learning_subjects").update({"completion_percentage": percentage}).eq("id", subject_id).execute()
            return True
        except Exception as e:
            st.error(f"Error updating learning subject progress: {e}")
            return False
    
    def delete_learning_subject(self, subject_id):
        try:
            # Delete related sessions first
            self.supabase.table("learning_sessions").delete().eq("subject_id", subject_id).execute()
            self.supabase.table("learning_milestones").delete().eq("subject_id", subject_id).execute()
            self.supabase.table("learning_subjects").delete().eq("id", subject_id).execute()
            return True
        except Exception as e:
            st.error(f"Error deleting learning subject: {e}")
            return False
    
    def get_learning_sessions(self, subject_id=None, days=None):
        try:
            query = self.supabase.table("learning_sessions").select("*")
            if subject_id:
                query = query.eq("subject_id", subject_id)
            if days:
                import datetime
                date_limit = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime('%Y-%m-%d')
                query = query.gte("date", date_limit)
            response = query.order("date", desc=True).execute()
            data = response.data
            if not data:
                return pd.DataFrame(columns=['id', 'subject_id', 'date', 'duration', 'content', 'notes', 'rating', 'created_at'])
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date']).dt.date if 'date' in df.columns else None
            return df
        except Exception as e:
            st.error(f"Error fetching learning sessions: {e}")
            return pd.DataFrame(columns=['id', 'subject_id', 'date', 'duration', 'content', 'notes', 'rating', 'created_at'])
    
    def add_learning_session(self, subject_id, date, duration, content, notes, rating):
        try:
            response = self.supabase.table("learning_sessions").insert({
                "subject_id": subject_id,
                "date": date,
                "duration": duration,
                "content": content,
                "notes": notes,
                "rating": rating
            }).execute()
            return response.data[0]['id'] if response.data else None
        except Exception as e:
            st.error(f"Error adding learning session: {e}")
            return None
    
    def delete_learning_session(self, session_id):
        try:
            self.supabase.table("learning_sessions").delete().eq("id", session_id).execute()
            return True
        except Exception as e:
            st.error(f"Error deleting learning session: {e}")
            return False
    
    def get_learning_milestones(self, subject_id=None):
        try:
            query = self.supabase.table("learning_milestones").select("*")
            if subject_id:
                query = query.eq("subject_id", subject_id)
            response = query.order("achieved_date", desc=True).execute()
            data = response.data
            if not data:
                return pd.DataFrame(columns=['id', 'subject_id', 'name', 'achieved_date', 'notes', 'created_at'])
            df = pd.DataFrame(data)
            df['achieved_date'] = pd.to_datetime(df['achieved_date']).dt.date if 'achieved_date' in df.columns else None
            return df
        except Exception as e:
            st.error(f"Error fetching learning milestones: {e}")
            return pd.DataFrame(columns=['id', 'subject_id', 'name', 'achieved_date', 'notes', 'created_at'])
    
    def add_learning_milestone(self, subject_id, name, achieved_date, notes):
        try:
            response = self.supabase.table("learning_milestones").insert({
                "subject_id": subject_id,
                "name": name,
                "achieved_date": achieved_date,
                "notes": notes
            }).execute()
            return response.data[0]['id'] if response.data else None
        except Exception as e:
            st.error(f"Error adding learning milestone: {e}")
            return None
    
    def delete_learning_milestone(self, milestone_id):
        try:
            self.supabase.table("learning_milestones").delete().eq("id", milestone_id).execute()
            return True
        except Exception as e:
            st.error(f"Error deleting learning milestone: {e}")
            return False