"""
Nutrition API client with Redis caching.
"""

import requests
import streamlit as st
import json
from src.cache import get_cache

class NutritionAPI:
    def __init__(self):
        try:
            self.api_key = st.secrets.get("RAPIDAPI_KEY", None)
        except:
            self.api_key = None
        
        self.base_url = "https://nutrition-tracker-api.p.rapidapi.com"
        self.headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": "nutrition-tracker-api.p.rapidapi.com",
            "Content-Type": "application/json"
        }
        
        # Initialize cache
        self.cache = get_cache()
        
        if self.api_key:
            print(f"🔑 API Key found: {self.api_key[:4]}...")
        else:
            print("❌ No API Key found!")
    
    def analyze_food(self, query):
        """
        Analyze a food query using Nutrition Tracker API.
        Checks cache first, then calls API.
        """
        if not self.api_key:
            st.error("❌ No API key found. Please add RAPIDAPI_KEY to secrets.")
            return None
        
        # Check cache first
        cached = self.cache.get_food(query)
        if cached:
            print(f"📦 Returning cached result for: {query}")
            return cached
        
        # Not in cache, call API
        print(f"🌐 Calling API for: {query}")
        result = self._call_api(query)
        
        if result and result.get('success'):
            # Only cache if data looks valid (carbs > 0 or calories > 0)
            if result.get('carbs', 0) > 0 or result.get('calories', 0) > 0:
                self.cache.set_food(query, result)
                print(f"💾 Cached result for: {query}")
            else:
                print(f"⚠️ Not caching result for: {query} (no valid data)")
        else:
            print(f"❌ API call failed for: {query}")
        
        return result
    
    def _call_api(self, query):
        """Call the actual API endpoint."""
        try:
            url = f"{self.base_url}/v1/calculate/natural"
            payload = {"text": query}
            
            print(f"📤 Sending request to: {url}")
            print(f"📤 Query: {query}")
            
            response = requests.post(
                url,
                json=payload,
                headers=self.headers,
                timeout=10
            )
            
            print(f"📥 Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success!")
                result = self._parse_response(data)
                
                # If carbs are 0 but calories > 0, still return the result
                # but don't cache it (handled in analyze_food)
                if result and result.get('carbs', 0) == 0 and result.get('calories', 0) > 0:
                    print(f"⚠️ Warning: Carbs = 0 but calories > 0. Not caching.")
                
                return result
            else:
                print(f"❌ Error: {response.status_code} - {response.text[:200]}")
                return None
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            return None
    
    def _parse_response(self, data):
        """Parse API response into standard format."""
        try:
            print(f"🔍 Parsing response...")
            
            # Check if there's an error
            if data.get('success') == False:
                error_msg = data.get('error', {}).get('message', 'Unknown error')
                print(f"❌ API Error: {error_msg}")
                return None
            
            # Try different response structures
            total_nutrients = {}
            
            if 'data' in data and 'totalNutrients' in data['data']:
                total_nutrients = data['data']['totalNutrients']
            elif 'totalNutrients' in data:
                total_nutrients = data['totalNutrients']
            else:
                for key, value in data.items():
                    if isinstance(value, dict) and 'value' in value:
                        total_nutrients[key] = value
            
            nutrient_names = list(total_nutrients.keys())
            print(f"📊 Available nutrients: {nutrient_names}")
            
            def get_nutrient(name):
                nutrient = total_nutrients.get(name, {})
                if isinstance(nutrient, dict):
                    return nutrient.get('value', 0)
                return float(nutrient) if nutrient else 0
            
            # Priority list for carbs
            carb_names = [
                'Carbohydrate, by difference',
                'Carbohydrates',
                'Total Carbohydrate',
                'Total Carbohydrates',
                'Carbohydrate',
            ]
            
            carbs = 0
            for name in carb_names:
                carbs = get_nutrient(name)
                if carbs > 0:
                    print(f"✅ Found carbs under '{name}': {carbs}")
                    break
            
            if carbs == 0:
                print(f"⚠️ Carbs not found. Available: {nutrient_names[:10]}")
            
            # Try to calculate carbs from calories if missing
            if carbs == 0:
                energy = get_nutrient('Energy')
                protein = get_nutrient('Protein')
                fat = get_nutrient('Fat')
                if energy > 0:
                    estimated = (energy - protein*4 - fat*9) / 4
                    if estimated > 0:
                        carbs = estimated
                        print(f"🔢 Estimated carbs: {carbs:.1f}g")
            
            result = {
                "calories": get_nutrient('Energy'),
                "protein": get_nutrient('Protein'),
                "carbs": carbs,
                "fat": get_nutrient('Fat'),
                "vitamin_a": get_nutrient('Vitamin A, RAE'),
                "vitamin_d": get_nutrient('Vitamin D (D2 + D3)'),
                "vitamin_c": get_nutrient('Vitamin C, total ascorbic acid'),
                "calcium": get_nutrient('Calcium, Ca'),
                "iron": get_nutrient('Iron, Fe'),
                "magnesium": get_nutrient('Magnesium, Mg'),
                "potassium": get_nutrient('Potassium, K'),
                "zinc": get_nutrient('Zinc, Zn'),
                "success": True,
                "raw": total_nutrients
            }
            
            print(f"✅ Parsed: {result['calories']} kcal, {result['protein']}g protein, {result['carbs']}g carbs, {result['fat']}g fat")
            return result
            
        except Exception as e:
            print(f"❌ Parse error: {e}")
            return None
    
    def invalidate_cache(self, query):
        """Delete a specific cache entry."""
        if self.cache.enabled:
            key = self.cache._get_key(query)
            try:
                self.cache.redis.delete(key)
                print(f"🗑️ Invalidated cache for: {query}")
                return True
            except Exception as e:
                print(f"⚠️ Failed to invalidate cache: {e}")
                return False
        return False