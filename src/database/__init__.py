import os
import sys
from .interface import DatabaseInterface
from src.config import Config

# Debug: Print which environment we're in
print(f"🔍 Config environment: {Config.get_env()}")

# Don't import Supabase at the top - import it only when needed

class SQLiteClient:
    """SQLite wrapper for development with all tables."""
    
    def __init__(self, db_path="finances.db"):
        self.db_path = db_path
        self._ensure_db_exists()
        self._ensure_tables()
    
    def _get_connection(self):
        """Get a database connection."""
        import sqlite3
        return sqlite3.connect(self.db_path)
    
    def _ensure_db_exists(self):
        """Create the database file if it doesn't exist."""
        import sqlite3
        # Create the directory if it doesn't exist
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.close()
    
    def _ensure_tables(self):
        """Create all tables if they don't exist."""
        import sqlite3
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # --- Transactions table ---
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Date TEXT NOT NULL,
                Deposit REAL DEFAULT 0,
                Withdrawal REAL DEFAULT 0
            )
        ''')
        
        # --- Food entries table ---
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS food_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Date TEXT NOT NULL,
                meal_type TEXT NOT NULL,
                food_name TEXT NOT NULL,
                calories INTEGER NOT NULL,
                protein REAL DEFAULT 0,
                carbs REAL DEFAULT 0,
                fat REAL DEFAULT 0,
                vitamin_a REAL DEFAULT 0,
                vitamin_c REAL DEFAULT 0,
                vitamin_d REAL DEFAULT 0,
                calcium REAL DEFAULT 0,
                iron REAL DEFAULT 0,
                magnesium REAL DEFAULT 0,
                zinc REAL DEFAULT 0,
                potassium REAL DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # --- Supplements table ---
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS supplements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Date TEXT NOT NULL,
                supplement_name TEXT NOT NULL,
                dosage REAL DEFAULT 0,
                unit TEXT DEFAULT 'mg',
                taken BOOLEAN DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # --- Vocabulary table ---
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vocabulary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL UNIQUE,
                cefr_level TEXT,
                definition TEXT,
                example_sentence TEXT,
                translation TEXT,
                importance INTEGER DEFAULT 3,
                mastery INTEGER DEFAULT 4,
                category TEXT,
                date_added TEXT,
                last_reviewed TEXT,
                times_reviewed INTEGER DEFAULT 0,
                next_review_date TEXT
            )
        ''')
        
        # --- Learning subjects table ---
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                priority TEXT,
                goal TEXT,
                status TEXT DEFAULT 'Not Started',
                start_date TEXT,
                target_date TEXT,
                completion_percentage INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # --- Learning sessions table ---
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id INTEGER,
                date TEXT NOT NULL,
                duration INTEGER NOT NULL,
                content TEXT,
                notes TEXT,
                rating INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (subject_id) REFERENCES learning_subjects(id)
            )
        ''')
        
        # --- Learning milestones table ---
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_milestones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id INTEGER,
                name TEXT NOT NULL,
                achieved_date TEXT,
                notes TEXT,
                FOREIGN KEY (subject_id) REFERENCES learning_subjects(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # --- Transaction methods ---
    
    def get_transactions(self, start_date=None, end_date=None):
        import sqlite3
        import pandas as pd
        conn = self._get_connection()
        query = "SELECT id, Date, Deposit, Withdrawal FROM transactions"
        params = []
        if start_date and end_date:
            query += " WHERE Date BETWEEN ? AND ?"
            params = [start_date, end_date]
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        if not df.empty and 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date']).dt.date
        return df
    
    def add_transaction(self, date, deposit, withdrawal):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO transactions (Date, Deposit, Withdrawal) VALUES (?, ?, ?)",
            (date, deposit, withdrawal)
        )
        conn.commit()
        conn.close()
        return cursor.lastrowid
    
    def update_transaction(self, id, date, deposit, withdrawal):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE transactions SET Date=?, Deposit=?, Withdrawal=? WHERE id=?",
            (date, deposit, withdrawal, id)
        )
        conn.commit()
        conn.close()
        return cursor.rowcount > 0
    
    def delete_transaction(self, id):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE id=?", (id,))
        conn.commit()
        conn.close()
        return cursor.rowcount > 0
    
    # --- Food entry methods ---
    
    def get_food_entries(self, date=None):
        import sqlite3
        import pandas as pd
        conn = self._get_connection()
        if date:
            df = pd.read_sql_query(
                "SELECT * FROM food_entries WHERE Date = ? ORDER BY id DESC",
                conn,
                params=[date]
            )
        else:
            df = pd.read_sql_query("SELECT * FROM food_entries ORDER BY Date DESC, id DESC", conn)
        conn.close()
        return df
    
    def add_food_entry(self, date, meal_type, food_name, calories, protein=0, carbs=0, fat=0,
                       vitamin_a=0, vitamin_c=0, vitamin_d=0, calcium=0, iron=0,
                       magnesium=0, zinc=0, potassium=0):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO food_entries (
                Date, meal_type, food_name, calories, protein, carbs, fat,
                vitamin_a, vitamin_c, vitamin_d, calcium, iron, magnesium, zinc, potassium
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            date, meal_type, food_name, calories, protein, carbs, fat,
            vitamin_a, vitamin_c, vitamin_d, calcium, iron, magnesium, zinc, potassium
        ))
        conn.commit()
        conn.close()
        return cursor.lastrowid
    
    # --- Supplement methods ---
    
    def get_supplements(self, start_date=None, end_date=None):
        import sqlite3
        import pandas as pd
        conn = self._get_connection()
        query = "SELECT * FROM supplements"
        params = []
        if start_date and end_date:
            query += " WHERE Date BETWEEN ? AND ?"
            params = [start_date, end_date]
        elif start_date:
            query += " WHERE Date = ?"
            params = [start_date]
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    
    def add_supplement(self, date, supplement_name, dosage, unit):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO supplements (Date, supplement_name, dosage, unit)
            VALUES (?, ?, ?, ?)
        ''', (date, supplement_name, dosage, unit))
        conn.commit()
        conn.close()
        return cursor.lastrowid
    
    def set_supplement_taken(self, date, supplement_name, dosage, unit, taken):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM supplements WHERE Date = ? AND supplement_name = ?",
            (date, supplement_name)
        )
        result = cursor.fetchone()
        if result:
            cursor.execute(
                "UPDATE supplements SET taken = ?, dosage = ?, unit = ? WHERE Date = ? AND supplement_name = ?",
                (taken, dosage, unit, date, supplement_name)
            )
        else:
            cursor.execute('''
                INSERT INTO supplements (Date, supplement_name, dosage, unit, taken)
                VALUES (?, ?, ?, ?, ?)
            ''', (date, supplement_name, dosage, unit, taken))
        conn.commit()
        conn.close()
        return True
    
    def delete_supplement(self, id):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM supplements WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        return cursor.rowcount > 0
    
    # --- Vocabulary methods ---
    
    def get_vocabulary(self, word=None):
        import sqlite3
        import pandas as pd
        conn = self._get_connection()
        if word:
            df = pd.read_sql_query("SELECT * FROM vocabulary WHERE word = ?", conn, params=[word])
        else:
            df = pd.read_sql_query("SELECT * FROM vocabulary ORDER BY word", conn)
        conn.close()
        return df
    
    def add_vocabulary(self, word, cefr_level, definition, example_sentence, translation=None,
                       importance=3, category="general", mastery=4, date_added=None, last_reviewed=None, next_review_date=None):
        import datetime
        conn = self._get_connection()
        cursor = conn.cursor()
        today = datetime.datetime.today().strftime('%Y-%m-%d')
        if not date_added:
            date_added = today
        if not last_reviewed:
            last_reviewed = today
        if not next_review_date:
            next_review_date = (datetime.datetime.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        cursor.execute('''
            INSERT INTO vocabulary (
                word, cefr_level, definition, example_sentence, translation,
                importance, category, mastery, date_added, last_reviewed, next_review_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (word, cefr_level, definition, example_sentence, translation, importance, category, mastery, date_added, last_reviewed, next_review_date))
        conn.commit()
        conn.close()
        return cursor.lastrowid
    
    def update_vocabulary_review(self, word, mastery):
        import datetime
        conn = self._get_connection()
        cursor = conn.cursor()
        today = datetime.datetime.today().strftime('%Y-%m-%d')
        # Calculate next review date based on mastery
        if mastery <= 2:
            days_to_add = 30
        elif mastery == 3:
            days_to_add = 14
        elif mastery == 4:
            days_to_add = 7
        else:
            days_to_add = 3
        next_review = (datetime.datetime.today() + datetime.timedelta(days=days_to_add)).strftime('%Y-%m-%d')
        cursor.execute('''
            UPDATE vocabulary
            SET mastery = ?,
                last_reviewed = ?,
                next_review_date = ?,
                times_reviewed = times_reviewed + 1
            WHERE word = ?
        ''', (mastery, today, next_review, word))
        conn.commit()
        conn.close()
        return cursor.rowcount > 0
    
    def delete_vocabulary(self, word):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM vocabulary WHERE word = ?", (word,))
        conn.commit()
        conn.close()
        return cursor.rowcount > 0
    
    # --- Learning methods ---
    
    def get_learning_subjects(self, status=None):
        import sqlite3
        import pandas as pd
        conn = self._get_connection()
        query = "SELECT * FROM learning_subjects"
        if status:
            query += f" WHERE status = '{status}'"
        query += " ORDER BY name"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def add_learning_subject(self, name, category, priority, goal, status, start_date, target_date):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO learning_subjects (name, category, priority, goal, status, start_date, target_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, category, priority, goal, status, start_date, target_date))
        conn.commit()
        conn.close()
        return cursor.lastrowid
    
    def update_learning_subject_status(self, subject_id, status):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE learning_subjects SET status = ? WHERE id = ?", (status, subject_id))
        conn.commit()
        conn.close()
    
    def update_learning_subject_progress(self, subject_id, percentage):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE learning_subjects SET completion_percentage = ? WHERE id = ?", (percentage, subject_id))
        conn.commit()
        conn.close()
    
    def delete_learning_subject(self, subject_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM learning_sessions WHERE subject_id = ?", (subject_id,))
        cursor.execute("DELETE FROM learning_milestones WHERE subject_id = ?", (subject_id,))
        cursor.execute("DELETE FROM learning_subjects WHERE id = ?", (subject_id,))
        conn.commit()
        conn.close()
    
    def get_learning_sessions(self, subject_id=None, days=None):
        import sqlite3
        import pandas as pd
        from datetime import datetime, timedelta
        conn = self._get_connection()
        query = "SELECT * FROM learning_sessions"
        params = []
        conditions = []
        if subject_id:
            conditions.append("subject_id = ?")
            params.append(subject_id)
        if days:
            date_limit = (datetime.today() - timedelta(days=days)).strftime('%Y-%m-%d')
            conditions.append("date >= ?")
            params.append(date_limit)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY date DESC"
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    
    def add_learning_session(self, subject_id, date, duration, content, notes, rating):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO learning_sessions (subject_id, date, duration, content, notes, rating)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (subject_id, date, duration, content, notes, rating))
        conn.commit()
        conn.close()
        return cursor.lastrowid
    
    def delete_learning_session(self, session_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM learning_sessions WHERE id = ?", (session_id,))
        conn.commit()
        conn.close()
    
    def get_learning_milestones(self, subject_id=None):
        import sqlite3
        import pandas as pd
        conn = self._get_connection()
        query = "SELECT * FROM learning_milestones"
        if subject_id:
            query += f" WHERE subject_id = {subject_id}"
        query += " ORDER BY achieved_date DESC"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def add_learning_milestone(self, subject_id, name, achieved_date, notes):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO learning_milestones (subject_id, name, achieved_date, notes)
            VALUES (?, ?, ?, ?)
        ''', (subject_id, name, achieved_date, notes))
        conn.commit()
        conn.close()
        return cursor.lastrowid
    
    def delete_learning_milestone(self, milestone_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM learning_milestones WHERE id = ?", (milestone_id,))
        conn.commit()
        conn.close()

def get_database():
    """Get the appropriate database client based on environment."""
    env = Config.get_env()
    print(f"🔍 Database environment: {env}")
    
    if env == "prod":
        print("🔍 Using Supabase (production)")
        from .supabase_client import SupabaseClient
        return SupabaseClient()
    else:
        print("🔍 Using SQLite (development)")
        # Use absolute path for SQLite in development
        db_path = os.path.expanduser("~/Mycode/MymoneyWeb/MymoneyWeb/finances.db")
        return SQLiteClient(db_path)

db = get_database()