"""
Vocabulary API using Free Dictionary API + Oxford 5000 word list.
"""

import requests
import streamlit as st
from .config import get_cefr_level, get_random_word_by_level
from .translation import TranslationService

class VocabularyAPI:
    def __init__(self):
        self.dict_api = "https://api.dictionaryapi.dev/api/v2/entries/en/"
        self.translator = TranslationService()
    
    def get_word_data(self, word):
        """Get CEFR level + definition + example + audio + translation."""
        word = word.lower().strip()
        
        cefr_level = get_cefr_level(word)
        api_data = self._get_from_dictionary_api(word)
        
        # Get translation with better error handling
        translation = None
        try:
            from .translation import TranslationService
            translator = TranslationService()
            translation = translator.translate_to_russian(word)
            print(f"🔍 Translation for '{word}': {translation}")
        except Exception as e:
            print(f"Translation error for '{word}': {e}")
        
        if api_data:
            return {
                "word": word,
                "cefr_level": cefr_level,
                "definition": api_data.get("definition", ""),
                "example": api_data.get("example", ""),
                "part_of_speech": api_data.get("part_of_speech", ""),
                "audio_url": api_data.get("audio_url", ""),
                "phonetic": api_data.get("phonetic", ""),
                "translation": translation,
                "found": True,
                "source": "dictionaryapi"
            }
        else:
            return {
                "word": word,
                "cefr_level": cefr_level,
                "definition": None,
                "example": None,
                "part_of_speech": None,
                "audio_url": None,
                "phonetic": None,
                "translation": translation,
                "found": False,
                "source": "oxford_only"
            }
    
    def _get_translation(self, word):
        """Get Russian translation for a word."""
        try:
            return self.translator.translate_to_russian(word)
        except Exception as e:
            print(f"Translation error for '{word}': {e}")
            return None
    
    def get_random_suggestion(self):
        """Get a random C1 or C2 word suggestion."""
        import random
        level = random.choice(["C1", "C2"])
        word = get_random_word_by_level(level)
        
        if word:
            data = self.get_word_data(word)
            data["suggested_level"] = level
            return data
        return None
    
    def _get_from_dictionary_api(self, word):
        """Fetch data from Free Dictionary API."""
        try:
            url = f"{self.dict_api}{word}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if data and len(data) > 0:
                    word_data = data[0]
                    
                    # Get phonetics and audio URL
                    phonetics = word_data.get("phonetics", [])
                    audio_url = None
                    phonetic = word_data.get("phonetic", "")
                    
                    for p in phonetics:
                        if p.get("audio"):
                            audio_url = p.get("audio")
                            break
                    
                    meanings = word_data.get("meanings", [])
                    
                    if meanings:
                        # Try to find a definition with an example
                        for meaning in meanings:
                            definitions = meaning.get("definitions", [])
                            for def_item in definitions:
                                if def_item.get("definition"):
                                    return {
                                        "definition": def_item.get("definition", ""),
                                        "example": def_item.get("example", ""),
                                        "part_of_speech": meaning.get("partOfSpeech", ""),
                                        "audio_url": audio_url,
                                        "phonetic": phonetic,
                                    }
                        
                        # If no definition with example, just take the first
                        first_meaning = meanings[0]
                        definitions = first_meaning.get("definitions", [])
                        if definitions:
                            first_def = definitions[0]
                            return {
                                "definition": first_def.get("definition", ""),
                                "example": first_def.get("example", ""),
                                "part_of_speech": first_meaning.get("partOfSpeech", ""),
                                "audio_url": audio_url,
                                "phonetic": phonetic,
                            }
            
            return None
        except Exception as e:
            print(f"Error fetching from dictionary API: {e}")
            return None