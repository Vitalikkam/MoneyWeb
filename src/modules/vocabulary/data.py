from src.database import db
import pandas as pd
from datetime import datetime, timedelta

def get_all_vocabulary():
    """Get all vocabulary words."""
    return db.get_vocabulary()

def get_vocabulary_by_word(word):
    """Get a specific word by name."""
    return db.get_vocabulary(word)

def add_vocabulary(word, cefr_level, definition, example, translation=None, 
                   importance=3, category="general", mastery=4):
    """Add a new vocabulary word."""
    return db.add_vocabulary(
        word, cefr_level, definition, example, translation,
        importance, category, mastery
    )

def update_review(word, mastery):
    """Update review status for a word."""
    return db.update_vocabulary_review(word, mastery)

def get_words_due_for_review():
    """Get words due for review."""
    return db.get_vocabulary_due()

def delete_vocabulary(word):
    """Delete a vocabulary word."""
    return db.delete_vocabulary(word)

def get_stats():
    """Get vocabulary statistics."""
    df = db.get_vocabulary()
    if df.empty:
        return {'total': 0, 'by_level': {}, 'due': 0, 'avg_mastery': 0}
    
    total = len(df)
    by_level = df['cefr_level'].value_counts().to_dict() if 'cefr_level' in df.columns else {}
    
    # Count due for review
    today = datetime.today().strftime('%Y-%m-%d')
    due = len(df[df['next_review_date'] <= today]) if 'next_review_date' in df.columns else 0
    
    avg_mastery = df['mastery'].mean() if 'mastery' in df.columns else 0
    
    return {
        'total': total,
        'by_level': by_level,
        'due': due,
        'avg_mastery': round(avg_mastery, 1)
    }

def word_exists(word):
    """Check if a word exists in vocabulary."""
    return db.word_exists(word)