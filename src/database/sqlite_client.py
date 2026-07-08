import sqlite3
import pandas as pd
from pathlib import Path
from .interface import DatabaseInterface

class SQLiteClient(DatabaseInterface):
    """SQLite implementation for local development."""
    
    def __init__(self, db_path="finances.db"):
        self.db_path = db_path
        self._ensure_db_exists()
        self._ensure_tables()
    
    def _get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def _ensure_db_exists(self):
        """Create data directory and database file if they don't exist."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
    
    def _ensure_tables(self):
        """Create all tables if they don't exist."""
        self._ensure_transactions_table()
        self._ensure_food_table()
    
    def _ensure_transactions_table(self):
        """Create transactions table if it doesn't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Date TEXT NOT NULL,
                Deposit REAL DEFAULT 0,
                Withdrawal REAL DEFAULT 0
            )
        ''')
        conn.commit()
        conn.close()
    
    def _ensure_food_table(self):
        """Create food_entries table with vitamins and minerals."""
        conn = self._get_connection()
        cursor = conn.cursor()
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
    
    # --- Transaction methods ---
    
    def get_transactions(self, start_date=None, end_date=None):
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

    def update_supplement_taken(self, date, supplement_name, taken):
        """Update whether a supplement was taken on a specific date."""
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
                "UPDATE supplements SET taken = ? WHERE Date = ? AND supplement_name = ?",
                (taken, date, supplement_name)
            )
        else:
            # Insert new
            return None
        
        conn.commit()
        conn.close()
        return cursor.rowcount > 0

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