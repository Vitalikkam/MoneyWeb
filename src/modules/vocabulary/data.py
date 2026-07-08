"""
Vocabulary data layer – CRUD operations for vocabulary entries.
"""

from src.database import db
import pandas as pd
from datetime import datetime, timedelta

def add_vocabulary(word, cefr_level, definition, example, importance=3, category="general", mastery=4):
    """Add a new vocabulary word."""
    try:
        conn = db._get_connection()
        cursor = conn.cursor()
        today = datetime.today().strftime('%Y-%m-%d')
        next_review = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        cursor.execute('''
            INSERT INTO vocabulary (
                word, cefr_level, definition, example_sentence,
                importance, category, mastery, date_added, last_reviewed, next_review_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (word, cefr_level, definition, example, importance, category, mastery, today, today, next_review))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error adding vocabulary: {e}")
        return False

def get_all_vocabulary():
    """Get all vocabulary words."""
    conn = db._get_connection()
    df = pd.read_sql_query("SELECT * FROM vocabulary ORDER BY word", conn)
    conn.close()
    return df

def get_words_due_for_review():
    """Get words due for review today."""
    today = datetime.today().strftime('%Y-%m-%d')
    conn = db._get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM vocabulary WHERE next_review_date <= ? ORDER BY next_review_date",
        conn,
        params=[today]
    )
    conn.close()
    return df

def update_review(word, mastery):
    """Update review status for a word."""
    today = datetime.today().strftime('%Y-%m-%d')
    
    # Calculate next review date based on mastery
    # Lower mastery = review sooner
    if mastery <= 2:
        days_to_add = 30
    elif mastery == 3:
        days_to_add = 14
    elif mastery == 4:
        days_to_add = 7
    else:
        days_to_add = 3
    
    next_review = (datetime.today() + timedelta(days=days_to_add)).strftime('%Y-%m-%d')
    
    conn = db._get_connection()
    cursor = conn.cursor()
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
    return True

def delete_vocabulary(word):
    """Delete a vocabulary word."""
    conn = db._get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vocabulary WHERE word = ?", (word,))
    conn.commit()
    conn.close()
    return True

def get_stats():
    """Get vocabulary statistics."""
    conn = db._get_connection()
    cursor = conn.cursor()
    
    # Total words
    cursor.execute("SELECT COUNT(*) FROM vocabulary")
    total = cursor.fetchone()[0]
    
    # By level
    cursor.execute("SELECT cefr_level, COUNT(*) FROM vocabulary GROUP BY cefr_level")
    by_level = cursor.fetchall()
    
    # Due for review
    today = datetime.today().strftime('%Y-%m-%d')
    cursor.execute("SELECT COUNT(*) FROM vocabulary WHERE next_review_date <= ?", (today,))
    due = cursor.fetchone()[0]
    
    # Mastery average
    cursor.execute("SELECT AVG(mastery) FROM vocabulary")
    avg_mastery = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return {
        'total': total,
        'by_level': dict(by_level),
        'due': due,
        'avg_mastery': round(avg_mastery, 1)
    }

def word_exists(word):
    """Check if a word already exists in vocabulary."""
    conn = db._get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM vocabulary WHERE word = ?", (word,))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0