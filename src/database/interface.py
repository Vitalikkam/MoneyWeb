from abc import ABC, abstractmethod
import pandas as pd

class DatabaseInterface(ABC):
    """Abstract base class defining the full database contract."""

    # --- Transactions ---

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

    # --- Food entries ---

    @abstractmethod
    def get_food_entries(self, date=None):
        pass

    @abstractmethod
    def add_food_entry(self, date, meal_type, food_name, calories,
                       protein=0, carbs=0, fat=0,
                       vitamin_a=0, vitamin_c=0, vitamin_d=0,
                       calcium=0, iron=0, magnesium=0, zinc=0, potassium=0):
        pass

    @abstractmethod
    def delete_food_entry(self, id):
        pass

    # --- Supplements ---

    @abstractmethod
    def get_supplements(self, start_date=None, end_date=None):
        pass

    @abstractmethod
    def set_supplement_taken(self, date, supplement_name, dosage, unit, taken):
        pass

    @abstractmethod
    def delete_supplement(self, id):
        pass

    # --- Vocabulary ---

    @abstractmethod
    def get_vocabulary(self):
        pass

    @abstractmethod
    def add_vocabulary(self, word, cefr_level, definition, example,
                       translation=None, importance=3, category='general', mastery=4):
        pass

    @abstractmethod
    def update_vocabulary_review(self, word, mastery, next_review_date):
        pass

    @abstractmethod
    def delete_vocabulary(self, word):
        pass

    @abstractmethod
    def word_exists(self, word):
        pass

    @abstractmethod
    def get_vocabulary_due(self, date):
        pass
