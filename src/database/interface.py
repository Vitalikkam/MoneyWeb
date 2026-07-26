from abc import ABC, abstractmethod
import pandas as pd

class DatabaseInterface(ABC):
    """Abstract base class for database implementations."""
    
    # --- Transaction methods ---
    @abstractmethod
    def get_transactions(self, start_date=None, end_date=None):
        pass
    
    @abstractmethod
    def add_transaction(self, date, deposit, withdrawal):
        pass
    
    @abstractmethod
    def update_transaction(self, id, date, deposit, withdrawal):
        pass
    
    @abstractmethod
    def delete_transaction(self, id):
        pass
    
    # --- Supplement methods ---
    @abstractmethod
    def get_supplements(self, start_date=None, end_date=None):
        pass
    
    @abstractmethod
    def add_supplement(self, date, supplement_name, dosage, unit):
        pass
    
    @abstractmethod
    def set_supplement_taken(self, date, supplement_name, dosage, unit, taken):
        pass
    
    @abstractmethod
    def delete_supplement(self, id):
        pass
    
    # --- Vocabulary methods ---
    @abstractmethod
    def get_vocabulary(self, word=None):
        pass
    
    @abstractmethod
    def add_vocabulary(self, word, cefr_level, definition, example_sentence, translation=None,
                       importance=3, category="general", mastery=4, date_added=None, last_reviewed=None, next_review_date=None):
        pass
    
    @abstractmethod
    def update_vocabulary_review(self, word, mastery):
        pass
    
    @abstractmethod
    def delete_vocabulary(self, word):
        pass
    
    @abstractmethod
    def get_vocabulary_due(self):
        pass
    
    @abstractmethod
    def word_exists(self, word):
        pass
    
    # --- Learning methods ---
    @abstractmethod
    def get_learning_subjects(self, status=None):
        pass
    
    @abstractmethod
    def add_learning_subject(self, name, category, priority, goal, status, start_date, target_date):
        pass
    
    @abstractmethod
    def update_learning_subject_status(self, subject_id, status):
        pass
    
    @abstractmethod
    def update_learning_subject_progress(self, subject_id, percentage):
        pass
    
    @abstractmethod
    def delete_learning_subject(self, subject_id):
        pass
    
    @abstractmethod
    def get_learning_sessions(self, subject_id=None, days=None):
        pass
    
    @abstractmethod
    def add_learning_session(self, subject_id, date, duration, content, notes, rating):
        pass
    
    @abstractmethod
    def delete_learning_session(self, session_id):
        pass
    
    @abstractmethod
    def get_learning_milestones(self, subject_id=None):
        pass
    
    @abstractmethod
    def add_learning_milestone(self, subject_id, name, achieved_date, notes):
        pass
    
    @abstractmethod
    def delete_learning_milestone(self, milestone_id):
        pass