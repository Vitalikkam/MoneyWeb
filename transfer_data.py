import sqlite3
import pandas as pd
from supabase import create_client
import os

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Please set SUPABASE_URL and SUPABASE_KEY environment variables")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Read local database
conn = sqlite3.connect('finances.db')
df = pd.read_sql_query("SELECT Date, Deposit, Withdrawal FROM transactions", conn)
conn.close()

print(f"📊 Found {len(df)} transactions to upload")

# Upload to Supabase (using lowercase column names)
success_count = 0
for i, row in df.iterrows():
    try:
        # Convert date to string in YYYY-MM-DD format
        date_str = row['Date'] if isinstance(row['Date'], str) else row['Date'].strftime('%Y-%m-%d')
        
        # Use lowercase column names to match Supabase
        data = {
            "date": date_str,        # lowercase 'date'
            "deposit": float(row['Deposit']),
            "withdrawal": float(row['Withdrawal'])
        }
        
        result = supabase.table("transactions").insert(data).execute()
        success_count += 1
        
        if (i + 1) % 10 == 0:
            print(f"✅ Uploaded {i + 1}/{len(df)} transactions")
    except Exception as e:
        print(f"❌ Error uploading row {i}: {e}")

print(f"✅ Done! Uploaded {success_count}/{len(df)} transactions to Supabase!")