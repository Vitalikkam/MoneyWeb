#!/usr/bin/env python3
"""
API Server for Finance Database
Runs on your Mac and exposes your finances.db via REST API.
Your data NEVER leaves your Mac – only query results are sent.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import pandas as pd
from datetime import datetime, date
import os
import json

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from Streamlit Cloud

# Database path (uses your existing finances.db)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "finances.db")

def get_connection():
    """Get a connection to your SQLite database."""
    return sqlite3.connect(DB_PATH)

def dict_factory(cursor, row):
    """Convert SQLite rows to dictionaries."""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

@app.route('/')
def home():
    """Health check endpoint."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM transactions")
        count = cursor.fetchone()[0]
        conn.close()
        return jsonify({
            "status": "Finance API is running!",
            "database": DB_PATH,
            "transactions": count,
            "message": "Your data is safe on your Mac"
        })
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    """
    Get all transactions.
    Returns: JSON array of transactions sorted by date.
    """
    try:
        conn = get_connection()
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, Date, Deposit, Withdrawal 
            FROM transactions 
            ORDER BY Date
        """)
        rows = cursor.fetchall()
        conn.close()
        
        # Convert dates to string format
        for row in rows:
            if 'Date' in row and row['Date']:
                row['Date'] = row['Date']  # SQLite returns string, keep as is
        
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    """
    Add a new transaction.
    Expected JSON: {"Date": "2026-06-29", "Deposit": 0.0, "Withdrawal": 0.0}
    """
    try:
        data = request.json
        date_str = data.get('Date')
        deposit = data.get('Deposit', 0.0)
        withdrawal = data.get('Withdrawal', 0.0)
        
        # Validate
        if not date_str:
            return jsonify({"error": "Date is required"}), 400
        if deposit < 0 or withdrawal < 0:
            return jsonify({"error": "Deposit and Withdrawal must be non-negative"}), 400
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO transactions (Date, Deposit, Withdrawal)
            VALUES (?, ?, ?)
        ''', (date_str, deposit, withdrawal))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        
        return jsonify({
            "status": "success",
            "id": new_id,
            "message": f"Transaction added successfully"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/transactions/<int:tx_id>', methods=['PUT'])
def update_transaction(tx_id):
    """
    Update an existing transaction.
    Expected JSON: {"Date": "2026-06-29", "Deposit": 0.0, "Withdrawal": 0.0}
    """
    try:
        data = request.json
        date_str = data.get('Date')
        deposit = data.get('Deposit', 0.0)
        withdrawal = data.get('Withdrawal', 0.0)
        
        if not date_str:
            return jsonify({"error": "Date is required"}), 400
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE transactions
            SET Date = ?, Deposit = ?, Withdrawal = ?
            WHERE id = ?
        ''', (date_str, deposit, withdrawal, tx_id))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        
        if affected == 0:
            return jsonify({"error": f"Transaction {tx_id} not found"}), 404
        
        return jsonify({
            "status": "success",
            "message": f"Transaction {tx_id} updated"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/transactions/<int:tx_id>', methods=['DELETE'])
def delete_transaction(tx_id):
    """Delete a transaction by ID."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM transactions WHERE id = ?', (tx_id,))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        
        if affected == 0:
            return jsonify({"error": f"Transaction {tx_id} not found"}), 404
        
        return jsonify({
            "status": "success",
            "message": f"Transaction {tx_id} deleted"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/summary', methods=['GET'])
def get_summary():
    """
    Get summary statistics: total deposits, withdrawals, balance.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                COALESCE(SUM(Deposit), 0) as total_deposits,
                COALESCE(SUM(Withdrawal), 0) as total_withdrawals,
                COALESCE(SUM(Deposit - Withdrawal), 0) as total_balance
            FROM transactions
        """)
        row = cursor.fetchone()
        conn.close()
        
        return jsonify({
            "total_deposits": row[0],
            "total_withdrawals": row[1],
            "total_balance": row[2]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/delete_all', methods=['DELETE'])
def delete_all():
    """
    Delete ALL transactions (use with caution!)
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM transactions')
        conn.commit()
        conn.close()
        return jsonify({
            "status": "success",
            "message": "All transactions deleted"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("💰 Finance API Server")
    print("=" * 60)
    print(f"Database: {DB_PATH}")
    print(f"Starting server on http://127.0.0.1:5000")
    print("")
    print("Available endpoints:")
    print("  GET  /                 - Health check")
    print("  GET  /api/transactions - Get all transactions")
    print("  POST /api/transactions - Add new transaction")
    print("  PUT  /api/transactions/<id> - Update transaction")
    print("  DELETE /api/transactions/<id> - Delete transaction")
    print("  GET  /api/summary      - Get summary statistics")
    print("")
    print("⚠️  Press Ctrl+C to stop the server")
    print("=" * 60)
    
    app.run(host='127.0.0.1', port=5000, debug=False)