from abc import ABC, abstractmethod
import pandas as pd

class DatabaseInterface(ABC):
    """Abstract base class for database implementations."""
    
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
    
    @abstractmethod
    def get_food_entries(self, date=None):
        pass
    
    @abstractmethod
    def add_food_entry(self, date, meal_type, food_name, calories, protein, carbs, fat):
        pass