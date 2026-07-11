"""
Translation service for vocabulary words using deep-translator (free).
"""

import streamlit as st
from deep_translator import GoogleTranslator

class TranslationService:
    def __init__(self):
        self.translator = GoogleTranslator(source='en', target='ru')
    
    def translate_to_russian(self, word):
        """Translate a word to Russian using GoogleTranslator."""
        try:
            translation = self.translator.translate(word)
            if translation:
                return translation
            return None
        except Exception as e:
            print(f"Translation error for '{word}': {e}")
            return None
    
    def translate_with_fallback(self, word):
        """Try to translate, return None if fails."""
        return self.translate_to_russian(word)