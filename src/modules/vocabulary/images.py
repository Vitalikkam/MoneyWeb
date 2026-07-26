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
            
            if response.status_code == 200:
                data = response.json()
                photos = data.get("photos", [])
                
                if photos:
                    # Pick a random photo from the results
                    photo = random.choice(photos)
                    image_url = photo.get("src", {}).get("medium")
                    
                    if image_url:
                        photographer = photo.get("photographer", "Unknown")
                        photographer_url = photo.get("photographer_url", "")
                        
                        print(f"✅ Found image for {word}")
                        return {
                            "url": image_url,
                            "emoji": emoji,
                            "source": "pexels",
                            "photographer": photographer,
                            "photographer_url": photographer_url,
                            "alt": f"Image of {word} by {photographer}"
                        }
                else:
                    print(f"⚠️ No photos found for {word}")
            
            # If API fails or no photos found, use emoji
            return {"url": None, "emoji": emoji, "source": "emoji"}
            
        except Exception as e:
            print(f"Error fetching image: {e}")
            return {"url": None, "emoji": emoji, "source": "emoji"}
    
    def display_image(self, word, width=400):
        """Display an image for a word."""
        image_data = self.get_image_url(word)
        
        if image_data.get("url"):
            # Display real image
            st.markdown(f"""
            <div style="text-align:center;margin:8px 0;">
                <img src="{image_data['url']}" alt="{image_data['alt']}" style="max-width:{width}px;width:100%;border-radius:12px;border:1px solid #2a3a4b;">
                <div style="color:#64748b;font-size:11px;margin-top:4px;">
                    📷 Photo by <a href="{image_data['photographer_url']}" target="_blank" style="color:#4ade80;text-decoration:none;">{image_data['photographer']}</a> on Pexels
                </div>
            </div>
            """, unsafe_allow_html=True)
        elif image_data.get("emoji"):
            # Display emoji fallback
            st.markdown(f"""
            <div style="text-align:center;font-size:80px;margin:8px 0;padding:20px;background:#0f172a;border-radius:12px;border:1px solid #2a3a4b;">
                {image_data['emoji']}
            </div>
            """, unsafe_allow_html=True)
        else:
            # No image available
            st.markdown(f"""
            <div style="text-align:center;font-size:40px;margin:8px 0;padding:20px;background:#0f172a;border-radius:12px;border:1px solid #2a3a4b;color:#64748b;">
                📚 No image available
            </div>
            """, unsafe_allow_html=True)
        
        return image_data