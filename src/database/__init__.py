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
        
        # Food entries table with vitamins and minerals
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
        
        conn.commit()
        conn.close()
    
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