import sqlite3
import pandas as pd
import streamlit as st

DB_PATH = "finances.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Date TEXT NOT NULL,
            Deposit REAL DEFAULT 0,
            Withdrawal REAL DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def get_all_transactions():
    conn = get_connection()
    df = pd.read_sql_query("SELECT id, Date, Deposit, Withdrawal FROM transactions ORDER BY Date", conn)
    conn.close()
    if not df.empty:
        df['Date'] = pd.to_datetime(df['Date']).dt.date
    return df

def save_dataframe(df):
    conn = get_connection()
    conn.execute("DELETE FROM transactions")
    if not df.empty:
        df_to_insert = df.copy()
        df_to_insert['Date'] = df_to_insert['Date'].astype(str)
        df_to_insert.to_sql('transactions', conn, if_exists='append', index=False)
    conn.commit()
    conn.close()

def clear_all_data():
    conn = get_connection()
    conn.execute("DELETE FROM transactions")
    conn.commit()
    conn.close()

def add_transaction(date, deposit, withdrawal):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO transactions (Date, Deposit, Withdrawal)
        VALUES (?, ?, ?)
    ''', (date.strftime('%Y-%m-%d'), deposit, withdrawal))
    conn.commit()
    conn.close()

# ---------- CSV IMPORT ----------
def parse_csv_columns(df):
    df = df.copy()
    cols_lower = {col.lower(): col for col in df.columns}
    
    # Date column
    date_col = None
    for key in ['date', 'transaction date', 'posting date', 'date posted', 'trans date']:
        if key in cols_lower:
            date_col = cols_lower[key]
            break
    if date_col:
        df['Date'] = pd.to_datetime(df[date_col], errors='coerce').dt.date
    else:
        st.warning("No date column found. Using today's date.")
        df['Date'] = pd.Timestamp.today().date()
    
    # Amount columns
    deposit_col = None
    withdrawal_col = None
    amount_col = None
    
    for key in ['deposit', 'credit', 'income', 'inflow', 'amount+', 'credit amount']:
        if key in cols_lower:
            deposit_col = cols_lower[key]
            break
    
    for key in ['withdrawal', 'debit', 'expense', 'outflow', 'amount-', 'debit amount']:
        if key in cols_lower:
            withdrawal_col = cols_lower[key]
            break
    
    if 'amount' in cols_lower and not deposit_col and not withdrawal_col:
        amount_col = cols_lower['amount']
    
    if amount_col:
        df['Amount'] = pd.to_numeric(df[amount_col], errors='coerce').fillna(0)
        df['Deposit'] = df['Amount'].apply(lambda x: x if x > 0 else 0)
        df['Withdrawal'] = df['Amount'].apply(lambda x: abs(x) if x < 0 else 0)
    else:
        if deposit_col:
            df['Deposit'] = pd.to_numeric(df[deposit_col], errors='coerce').fillna(0)
        else:
            df['Deposit'] = 0.0
        if withdrawal_col:
            df['Withdrawal'] = pd.to_numeric(df[withdrawal_col], errors='coerce').fillna(0)
        else:
            df['Withdrawal'] = 0.0
    
    df = df[(df['Deposit'] != 0) | (df['Withdrawal'] != 0)]
    return df[['Date', 'Deposit', 'Withdrawal']]

def append_csv_data(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)
        if df.empty:
            return False, "The CSV file is empty.", 0
        parsed_df = parse_csv_columns(df)
        if parsed_df.empty:
            return False, "No valid transactions found.", 0
        
        conn = get_connection()
        parsed_df_to_insert = parsed_df.copy()
        parsed_df_to_insert['Date'] = parsed_df_to_insert['Date'].astype(str)
        parsed_df_to_insert.to_sql('transactions', conn, if_exists='append', index=False)
        conn.commit()
        conn.close()
        return True, f"Successfully imported {len(parsed_df)} transactions.", len(parsed_df)
    except Exception as e:
        return False, f"Error importing CSV: {str(e)}", 0

# ---------- CSV EXPORT ----------
def export_to_csv():
    df = get_all_transactions()
    if df.empty:
        return None
    df_export = df.drop(columns=['id'], errors='ignore')
    df_export['Date'] = df_export['Date'].astype(str)
    return df_export.to_csv(index=False).encode('utf-8')