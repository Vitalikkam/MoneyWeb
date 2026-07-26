import streamlit as st
import os

class ProdConfig:
    def get_env(self):
        return "prod"
    
    @staticmethod
    def get_supabase_url():
        # Try secrets first, then environment variable
        try:
            return st.secrets["prod"]["SUPABASE_URL"]
        except:
            return os.getenv("SUPABASE_URL")
    
    @staticmethod
    def get_supabase_key():
        try:
            return st.secrets["prod"]["SUPABASE_KEY"]
        except:
            return os.getenv("SUPABASE_KEY")