"""
Learning module – CRUD operations for subjects, sessions, and milestones.
"""

from src.database import db
import pandas as pd
from datetime import datetime, timedelta

# ---------- SUBJECTS ----------
def add_subject(name, category=None, priority=None, goal=None, status="Not Started", target_date=None):
    """Add a new learning subject."""
    conn = db._get_connection()
    cursor = conn.cursor()
    start_date = datetime.today().strftime('%Y-%m-%d')
    cursor.execute('''
        INSERT INTO learning_subjects (name, category, priority, goal, status, start_date, target_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name, category, priority, goal, status, start_date, target_date))
    conn.commit()
    conn.close()
    return cursor.lastrowid

def get_subjects(status=None):
    """Get all learning subjects, optionally filtered by status."""
    conn = db._get_connection()
    query = "SELECT * FROM learning_subjects"
    if status:
        query += f" WHERE status = '{status}'"
    query += " ORDER BY name"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_subject(subject_id):
    """Get a single subject by ID."""
    conn = db._get_connection()
    df = pd.read_sql_query("SELECT * FROM learning_subjects WHERE id = ?", conn, params=[subject_id])
    conn.close()
    return df.iloc[0] if not df.empty else None

def update_subject_status(subject_id, status):
    """Update subject status."""
    conn = db._get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE learning_subjects SET status = ? WHERE id = ?", (status, subject_id))
    conn.commit()
    conn.close()

def update_subject_progress(subject_id, percentage):
    """Update subject completion percentage."""
    conn = db._get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE learning_subjects SET completion_percentage = ? WHERE id = ?", (percentage, subject_id))
    conn.commit()
    conn.close()

def delete_subject(subject_id):
    """Delete a subject and all related sessions."""
    conn = db._get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM learning_sessions WHERE subject_id = ?", (subject_id,))
    cursor.execute("DELETE FROM learning_milestones WHERE subject_id = ?", (subject_id,))
    cursor.execute("DELETE FROM learning_subjects WHERE id = ?", (subject_id,))
    conn.commit()
    conn.close()

# ---------- SESSIONS ----------
def add_session(subject_id, duration, content=None, notes=None, rating=None):
    """Log a study session."""
    conn = db._get_connection()
    cursor = conn.cursor()
    date = datetime.today().strftime('%Y-%m-%d')
    cursor.execute('''
        INSERT INTO learning_sessions (subject_id, date, duration, content, notes, rating)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (subject_id, date, duration, content, notes, rating))
    conn.commit()
    conn.close()
    return cursor.lastrowid

def get_sessions(subject_id=None, days=None):
    """Get study sessions, optionally filtered by subject or days."""
    conn = db._get_connection()
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

def get_total_hours(subject_id):
    """Get total study hours for a subject."""
    conn = db._get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(duration) FROM learning_sessions WHERE subject_id = ?", (subject_id,))
    total_minutes = cursor.fetchone()[0] or 0
    conn.close()
    return round(total_minutes / 60, 1)

def get_study_streak():
    """Calculate current study streak in days."""
    conn = db._get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT date FROM learning_sessions ORDER BY date DESC")
    dates = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    if not dates:
        return 0
    
    streak = 0
    current_date = datetime.today().date()
    
    for date_str in dates:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        if date_obj == current_date:
            streak += 1
            current_date -= timedelta(days=1)
        elif date_obj == current_date:
            streak += 1
            current_date -= timedelta(days=1)
        else:
            break
    
    return streak

def delete_session(session_id):
    """Delete a study session."""
    conn = db._get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM learning_sessions WHERE id = ?", (session_id,))
    conn.commit()
    conn.close()

# ---------- MILESTONES ----------
def add_milestone(subject_id, name, notes=None):
    """Add a milestone for a subject."""
    conn = db._get_connection()
    cursor = conn.cursor()
    achieved_date = datetime.today().strftime('%Y-%m-%d')
    cursor.execute('''
        INSERT INTO learning_milestones (subject_id, name, achieved_date, notes)
        VALUES (?, ?, ?, ?)
    ''', (subject_id, name, achieved_date, notes))
    conn.commit()
    conn.close()
    return cursor.lastrowid

def get_milestones(subject_id=None):
    """Get milestones, optionally filtered by subject."""
    conn = db._get_connection()
    query = "SELECT * FROM learning_milestones"
    if subject_id:
        query += f" WHERE subject_id = {subject_id}"
    query += " ORDER BY achieved_date DESC"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def delete_milestone(milestone_id):
    """Delete a milestone."""
    conn = db._get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM learning_milestones WHERE id = ?", (milestone_id,))
    conn.commit()
    conn.close()