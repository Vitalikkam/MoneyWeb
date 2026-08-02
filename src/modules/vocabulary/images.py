"""
Image API integration for vocabulary words using Pexels API.
"""

import requests
import streamlit as st
import random
from .emoji import get_emoji


@st.cache_data(ttl=3600, show_spinner=False)
def _fetch_pexels_image(word: str, api_key: str):
    """Fetch an image from Pexels for a word. Cached for 1 hour."""
    try:
        url = "https://api.pexels.com/v1/search"
        params = {"query": word, "per_page": 5, "orientation": "landscape", "size": "medium"}
        response = requests.get(url, params=params, headers={"Authorization": api_key}, timeout=5)

        if response.status_code == 200:
            photos = response.json().get("photos", [])
            if photos:
                photo = random.choice(photos)
                image_url = photo.get("src", {}).get("medium")
                if image_url:
                    return {
                        "url": image_url,
                        "source": "pexels",
                        "photographer": photo.get("photographer", "Unknown"),
                        "photographer_url": photo.get("photographer_url", ""),
                        "alt": f"Image of {word}"
                    }
    except Exception as e:
        print(f"Error fetching image for '{word}': {e}")
    return None


class ImageAPI:
    def __init__(self):
        try:
            # Try nested under [prod] section first (production), then fall back to top-level (dev)
            self.api_key = st.secrets.get("prod", {}).get("PEXELS_API_KEY") or st.secrets.get("PEXELS_API_KEY", None)
        except Exception:
            self.api_key = None

        if self.api_key:
            print("🔑 Pexels API Key found")
        else:
            print("⚠️ No Pexels API Key found. Using emoji fallback.")

    def get_image_url(self, word):
        """Get an image URL for a word. Uses cache to avoid repeated requests."""
        emoji = get_emoji(word)

        if not self.api_key:
            return {"url": None, "emoji": emoji, "source": "emoji"}

        result = _fetch_pexels_image(word, self.api_key)
        if result:
            result["emoji"] = emoji
            return result

        return {"url": None, "emoji": emoji, "source": "emoji"}

    def display_image(self, word, width=400):
        """Display an image for a word."""
        image_data = self.get_image_url(word)

        if image_data.get("url"):
            st.markdown(
                f'<div style="text-align:center;margin:8px 0;">'
                f'<img src="{image_data["url"]}" alt="{image_data.get("alt","")}" style="max-width:{width}px;width:100%;border-radius:12px;border:1px solid #2a3a4b;">'
                f'<div style="color:#64748b;font-size:11px;margin-top:4px;">📷 Photo by '
                f'<a href="{image_data["photographer_url"]}" target="_blank" style="color:#4ade80;text-decoration:none;">{image_data["photographer"]}</a>'
                f' on Pexels</div></div>',
                unsafe_allow_html=True
            )
        elif image_data.get("emoji"):
            st.markdown(
                f'<div style="text-align:center;font-size:80px;margin:8px 0;padding:20px;background:#0f172a;border-radius:12px;border:1px solid #2a3a4b;">{image_data["emoji"]}</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<div style="text-align:center;font-size:40px;margin:8px 0;padding:20px;background:#0f172a;border-radius:12px;border:1px solid #2a3a4b;color:#64748b;">📚 No image available</div>',
                unsafe_allow_html=True
            )

        return image_data