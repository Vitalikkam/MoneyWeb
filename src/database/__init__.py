from .interface import DatabaseInterface
from src.config import Config

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
        conn = sqlite3.connect(self.db_path)
        conn.close()
    
    def _ensure_tables(self):
        """Create all tables if they don't exist."""
        import sqlite3
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Date TEXT NOT NULL,
                Deposit REAL DEFAULT 0,
                Withdrawal REAL DEFAULT 0
            )
        ''')
        
        # Food entries table
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
        
        # Supplements table
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

        # Vocabulary table
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
        # Convert Date to datetime
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
        """Add a food entry with vitamins and minerals."""
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
        """Get supplements for a date range."""
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
        """Add a supplement entry."""
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
        """Set supplement taken status (insert or update)."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Check if entry exists
        cursor.execute(
            "SELECT id FROM supplements WHERE Date = ? AND supplement_name = ?",
            (date, supplement_name)
        )
        result = cursor.fetchone()
        
        if result:
            # Update existing
            cursor.execute(
                "UPDATE supplements SET taken = ?, dosage = ?, unit = ? WHERE Date = ? AND supplement_name = ?",
                (taken, dosage, unit, date, supplement_name)
            )
        else:
            # Insert new
            cursor.execute('''
                INSERT INTO supplements (Date, supplement_name, dosage, unit, taken)
                VALUES (?, ?, ?, ?, ?)
            ''', (date, supplement_name, dosage, unit, taken))
        
        conn.commit()
        conn.close()
        return True
    
    def delete_supplement(self, id):
        """Delete a supplement entry by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM supplements WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        return cursor.rowcount > 0

    # --- Food entry delete ---

    def delete_food_entry(self, id):
        """Delete a food entry by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM food_entries WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        return cursor.rowcount > 0

    # --- Vocabulary methods ---

    def get_vocabulary(self):
        """Get all vocabulary words."""
        import pandas as pd
        conn = self._get_connection()
        df = pd.read_sql_query("SELECT * FROM vocabulary ORDER BY word", conn)
        conn.close()
        return df

    def add_vocabulary(self, word, cefr_level, definition, example,
                       translation=None, importance=3, category='general', mastery=4):
        """Add a new vocabulary word."""
        from datetime import datetime, timedelta
        today = datetime.today().strftime('%Y-%m-%d')
        next_review = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO vocabulary (
                    word, cefr_level, definition, example_sentence, translation,
                    importance, category, mastery, date_added, last_reviewed, next_review_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (word, cefr_level, definition, example, translation,
                  importance, category, mastery, today, today, next_review))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            print(f"Error adding vocabulary: {e}")
            return False

    def update_vocabulary_review(self, word, mastery, next_review_date):
        """Update review status for a word."""
        from datetime import datetime
        today = datetime.today().strftime('%Y-%m-%d')
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE vocabulary
            SET mastery = ?, last_reviewed = ?, next_review_date = ?,
                times_reviewed = times_reviewed + 1
            WHERE word = ?
        ''', (mastery, today, next_review_date, word))
        conn.commit()
        conn.close()
        return cursor.rowcount > 0

    def delete_vocabulary(self, word):
        """Delete a vocabulary word."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM vocabulary WHERE word = ?", (word,))
        conn.commit()
        conn.close()
        return cursor.rowcount > 0

    def word_exists(self, word):
        """Check if a word already exists."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM vocabulary WHERE word = ?", (word,))
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0

    def get_vocabulary_due(self, date):
        """Get vocabulary words due for review on or before a date."""
        import pandas as pd
        conn = self._get_connection()
        df = pd.read_sql_query(
            "SELECT * FROM vocabulary WHERE next_review_date <= ? ORDER BY next_review_date",
            conn, params=[date]
        )
        conn.close()
        return df

def get_database():
    """Get the appropriate database client based on environment."""
    env = Config.get_env()
    if env == "prod":
        # Import Supabase only when needed
        from .supabase_client import SupabaseClient
        return SupabaseClient()
    else:
        return SQLiteClient("finances.db")

db = get_database()