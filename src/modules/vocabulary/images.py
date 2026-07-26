"""
Image API integration for vocabulary words using Pexels API.
"""

import requests
import streamlit as st
import random
from .emoji import get_emoji

class ImageAPI:
    def __init__(self):
        try:
            self.api_key = st.secrets.get("PEXELS_API_KEY", None)
        except:
            self.api_key = None
        
        self.base_url = "https://api.pexels.com/v1"
        self.headers = {"Authorization": self.api_key} if self.api_key else {}
        
        if self.api_key:
            print("🔑 Pexels API Key found")
        else:
            print("⚠️ No Pexels API Key found. Using emoji fallback.")
    
    def get_image_url(self, word):
        """Get an image URL for a word from Pexels API."""
        # First check if we have an emoji fallback
        emoji = get_emoji(word)
        
        if not self.api_key:
            print(f"❌ No Pexels API key for '{word}'")
            return {"url": None, "emoji": emoji, "source": "emoji"}
        
        try:
            # Search for the word
            url = f"{self.base_url}/search"
            params = {
                "query": word,
                "per_page": 5,
                "orientation": "landscape",
                "size": "medium"
            }
            
            print(f"🔍 Searching Pexels for: {word}")
            response = requests.get(url, params=params, headers=self.headers, timeout=5)
            print(f"📡 Pexels response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                photos = data.get("photos", [])
                print(f"📸 Found {len(photos)} photos for '{word}'")
                
                if photos:
                    # Pick a random photo from the results
                    photo = random.choice(photos)
                    image_url = photo.get("src", {}).get("medium")
                    
                    if image_url:
                        photographer = photo.get("photographer", "Unknown")
                        photographer_url = photo.get("photographer_url", "")
                        
                        print(f"✅ Image URL: {image_url[:50]}...")
                        return {
                            "url": image_url,
                            "emoji": emoji,
                            "source": "pexels",
                            "photographer": photographer,
                            "photographer_url": photographer_url,
                            "alt": f"Image of {word} by {photographer}"
                        }
            else:
                print(f"❌ Pexels API error: {response.status_code}")
                if response.status_code == 401:
                    print("❌ Invalid Pexels API key!")
            
            # If API fails or no photos found, use emoji
            return {"url": None, "emoji": emoji, "source": "emoji"}
            
        except Exception as e:
            print(f"❌ Error fetching image: {e}")
            return {"url": None, "emoji": emoji, "source": "emoji"}