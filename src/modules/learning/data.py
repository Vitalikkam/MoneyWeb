from src.database import db
import pandas as pd
from datetime import datetime, timedelta

def get_subjects(status=None):
    """Get all learning subjects."""
    return db.get_learning_subjects(status)

def add_subject(name, category=None, priority=None, goal=None, status="Not Started", target_date=None):
    """Add a new learning subject."""
    start_date = datetime.today().strftime('%Y-%m-%d')
    return db.add_learning_subject(name, category, priority, goal, status, start_date, target_date)

def get_subject(subject_id):
    """Get a single subject by ID."""
    df = db.get_learning_subjects()
    if df.empty:
        return None
    result = df[df['id'] == subject_id]
    return result.iloc[0] if not result.empty else None

def update_subject_status(subject_id, status):
    """Update subject status."""
    return db.update_learning_subject_status(subject_id, status)

def update_subject_progress(subject_id, percentage):
    """Update subject completion percentage."""
    return db.update_learning_subject_progress(subject_id, percentage)

def delete_subject(subject_id):
    """Delete a subject and all related sessions."""
    return db.delete_learning_subject(subject_id)

def get_sessions(subject_id=None, days=None):
    """Get study sessions."""
    return db.get_learning_sessions(subject_id, days)

def add_session(subject_id, duration, content=None, notes=None, rating=None):
    """Log a study session."""
    date = datetime.today().strftime('%Y-%m-%d')
    return db.add_learning_session(subject_id, date, duration, content, notes, rating)

def delete_session(session_id):
    """Delete a study session."""
    return db.delete_learning_session(session_id)

def get_milestones(subject_id=None):
    """Get milestones."""
    return db.get_learning_milestones(subject_id)

def add_milestone(subject_id, name, notes=None):
    """Add a milestone for a subject."""
    achieved_date = datetime.today().strftime('%Y-%m-%d')
    return db.add_learning_milestone(subject_id, name, achieved_date, notes)

def delete_milestone(milestone_id):
    """Delete a milestone."""
    return db.delete_learning_milestone(milestone_id)

def get_total_hours(subject_id):
    """Get total study hours for a subject."""
    sessions = db.get_learning_sessions(subject_id)
    if sessions.empty:
        return 0
    return round(sessions['duration'].sum() / 60, 1)

def get_study_streak():
    """Calculate current study streak in days."""
    sessions = db.get_learning_sessions()
    if sessions.empty:
        return 0
    
    dates = pd.to_datetime(sessions['date']).dt.date.sort_values(ascending=False).unique()
    
    streak = 0
    current_date = datetime.today().date()
    
    for date_obj in dates:
        if date_obj == current_date:
            streak += 1
            current_date -= timedelta(days=1)
        else:
            break
    
    return streak