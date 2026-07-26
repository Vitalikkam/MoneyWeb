from supabase import create_client
import streamlit as st
import pandas as pd
from .interface import DatabaseInterface
from datetime import datetime, timedelta

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
                query = query.gte("date", start_date).lte("date", end_date)
            response = query.order("date").execute()
            data = response.data
            if not data:
                return pd.DataFrame(columns=['id', 'Date', 'Deposit', 'Withdrawal'])
            df = pd.DataFrame(data)
            df['Date'] = pd.to_datetime(df['date']).dt.date
            return df
        except Exception as e:
            st.error(f"Error fetching transactions: {e}")
            return pd.DataFrame(columns=['id', 'Date', 'Deposit', 'Withdrawal'])
    
    def add_transaction(self, date, deposit, withdrawal):
        try:
            self.supabase.table("transactions").insert({
                "date": date,
                "deposit": float(deposit),
                "withdrawal": float(withdrawal)
            }).execute()
            return True
        except Exception as e:
            st.error(f"Error adding transaction: {e}")
            return False
    
    def update_transaction(self, id, date, deposit, withdrawal):
        try:
            self.supabase.table("transactions").update({
                "date": date,
                "deposit": float(deposit),
                "withdrawal": float(withdrawal)
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
    # SUPPLEMENT METHODS
    # ============================================
    
    def get_supplements(self, start_date=None, end_date=None):
        try:
            query = self.supabase.table("supplements").select("*")
            if start_date and end_date:
                query = query.gte("date", start_date).lte("date", end_date)
            elif start_date:
                query = query.eq("date", start_date)
            response = query.execute()
            data = response.data
            if not data:
                return pd.DataFrame(columns=['id', 'Date', 'supplement_name', 'dosage', 'unit', 'taken'])
            df = pd.DataFrame(data)
            df['Date'] = pd.to_datetime(df['date']).dt.date
            return df
        except Exception as e:
            st.error(f"Error fetching supplements: {e}")
            return pd.DataFrame(columns=['id', 'Date', 'supplement_name', 'dosage', 'unit', 'taken'])
    
    def add_supplement(self, date, supplement_name, dosage, unit):
        try:
            self.supabase.table("supplements").insert({
                "date": date,
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
            response = self.supabase.table("supplements").select("id").eq("date", date).eq("supplement_name", supplement_name).execute()
            
            if response.data:
                # Update existing
                self.supabase.table("supplements").update({
                    "taken": taken,
                    "dosage": float(dosage),
                    "unit": unit
                }).eq("date", date).eq("supplement_name", supplement_name).execute()
            else:
                # Insert new
                self.supabase.table("supplements").insert({
                    "date": date,
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
                "next_review_date": next_review
            }).eq("word", word).execute()
            
            # Increment times_reviewed
            try:
                current = self.supabase.table("vocabulary").select("times_reviewed").eq("word", word).execute()
                if current.data:
                    times = current.data[0].get('times_reviewed', 0) + 1
                    self.supabase.table("vocabulary").update({
                        "times_reviewed": times
                    }).eq("word", word).execute()
            except:
                pass
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
    
    def get_vocabulary_due(self):
        """Get vocabulary words due for review."""
        try:
            today = datetime.today().strftime('%Y-%m-%d')
            response = self.supabase.table("vocabulary").select("*").lte("next_review_date", today).execute()
            data = response.data
            if not data:
                return pd.DataFrame(columns=['id', 'word', 'cefr_level', 'definition', 'example_sentence', 'translation', 'importance', 'mastery', 'category', 'date_added', 'last_reviewed', 'times_reviewed', 'next_review_date'])
            df = pd.DataFrame(data)
            return df
        except Exception as e:
            st.error(f"Error fetching vocabulary due: {e}")
            return pd.DataFrame(columns=['id', 'word', 'cefr_level', 'definition', 'example_sentence', 'translation', 'importance', 'mastery', 'category', 'date_added', 'last_reviewed', 'times_reviewed', 'next_review_date'])
    
    def word_exists(self, word):
        """Check if a word exists in vocabulary."""
        try:
            response = self.supabase.table("vocabulary").select("id").eq("word", word).execute()
            return len(response.data) > 0
        except Exception as e:
            st.error(f"Error checking word exists: {e}")
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
                date_limit = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
                query = query.gte("date", date_limit)
            response = query.order("date", desc=True).execute()
            data = response.data
            if not data:
                return pd.DataFrame(columns=['id', 'subject_id', 'date', 'duration', 'content', 'notes', 'rating', 'created_at'])
            df = pd.DataFrame(data)
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