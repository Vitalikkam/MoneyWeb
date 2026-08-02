from src.database import db
import pandas as pd
from datetime import datetime


def log_exercise(date, workout_type, notes, energy_level):
    """Log a workout session."""
    return db.add_exercise(date, workout_type, notes, energy_level)


def get_exercises(days=None):
    """Get exercise log, optionally limited to last N days."""
    return db.get_exercises(days=days)


def delete_exercise(exercise_id):
    """Delete an exercise log entry."""
    return db.delete_exercise(exercise_id)


def get_streak():
    """Calculate current workout streak in days."""
    df = db.get_exercises()
    if df.empty:
        return 0

    dates = sorted(pd.to_datetime(df['date']).dt.date.unique(), reverse=True)
    today = datetime.today().date()
    streak = 0

    for i, d in enumerate(dates):
        expected = today - pd.Timedelta(days=i)
        if d == expected:
            streak += 1
        else:
            break

    return streak


def get_stats():
    """Get exercise statistics."""
    df = db.get_exercises()
    if df.empty:
        return {
            'total_workouts': 0,
            'this_week': 0,
            'this_month': 0,
            'streak': 0,
            'avg_duration': 0,
            'by_type': {},
        }

    today = datetime.today().date()
    df['date_parsed'] = pd.to_datetime(df['date']).dt.date

    week_start = today - pd.Timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    this_week = len(df[df['date_parsed'] >= week_start])
    this_month = len(df[df['date_parsed'] >= month_start])

    by_type = df['workout_type'].value_counts().to_dict() if 'workout_type' in df.columns else {}

    return {
        'total_workouts': len(df),
        'this_week': this_week,
        'this_month': this_month,
        'streak': get_streak(),
        'by_type': by_type,
    }
