"""
Nutrition API client with manual fallback.
"""

import requests
import streamlit as st
import json

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
        
        if self.api_key:
            print(f"🔑 API Key found: {self.api_key[:4]}...")
        else:
            print("❌ No API Key found!")
    
    def analyze_food(self, query):
        """
        Analyze a food query using Nutrition Tracker API.
        """
        if not self.api_key:
            st.error("❌ No API key found. Please add RAPIDAPI_KEY to secrets.")
            return None
        
        result = self._try_endpoint("/v1/calculate/natural", query)
        if result:
            return result
        
        st.error("❌ Could not analyze food. Please try manual entry.")
        return None
    
    def _try_endpoint(self, endpoint, query):
        """Try a specific endpoint."""
        try:
            url = f"{self.base_url}{endpoint}"
            payload = {"text": query}
            
            print(f"📤 Trying endpoint: {endpoint}")
            print(f"📤 Payload: {payload}")
            
            response = requests.post(
                url,
                json=payload,
                headers=self.headers,
                timeout=10
            )
            
            print(f"📥 Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success with {endpoint}!")
                return self._parse_response(data)
            else:
                print(f"❌ {endpoint} failed: {response.status_code}")
                print(f"❌ Response: {response.text[:200]}")
                return None
                
        except Exception as e:
            print(f"❌ {endpoint} error: {e}")
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
                # Try to find nutrients in the data
                for key, value in data.items():
                    if isinstance(value, dict) and 'value' in value:
                        total_nutrients[key] = value
            
            # Debug: Print available nutrients
            nutrient_names = list(total_nutrients.keys())
            print(f"📊 Available nutrients: {nutrient_names}")
            
            def get_nutrient(name):
                nutrient = total_nutrients.get(name, {})
                if isinstance(nutrient, dict):
                    return nutrient.get('value', 0)
                return float(nutrient) if nutrient else 0
            
            # Try multiple names for carbs
            carb_names = [
                'Carbohydrates',
                'Carbohydrate, by difference',
                'Carbohydrate',
                'Total Carbohydrate',
                'Total Carbohydrates',
                'Carbs',
                'carbohydrate',
                'Carbohydrates'
            ]
            
            carbs = 0
            for name in carb_names:
                carbs = get_nutrient(name)
                if carbs > 0:
                    print(f"✅ Found carbs under '{name}': {carbs}")
                    break
            
            if carbs == 0:
                print(f"⚠️ Carbs not found. Available: {nutrient_names[:10]}")
            
            # Try alternative names for protein
            protein_names = ['Protein', 'protein']
            protein = 0
            for name in protein_names:
                protein = get_nutrient(name)
                if protein > 0:
                    print(f"✅ Found protein under '{name}': {protein}")
                    break
            
            # Try alternative names for fat
            fat_names = ['Fat', 'Total lipid (fat)', 'fat']
            fat = 0
            for name in fat_names:
                fat = get_nutrient(name)
                if fat > 0:
                    print(f"✅ Found fat under '{name}': {fat}")
                    break
            
            result = {
                # Macros
                "calories": get_nutrient('Energy'),
                "protein": protein,
                "carbs": carbs,
                "fat": fat,
                
                # Vitamins
                "vitamin_a": get_nutrient('Vitamin A, RAE'),
                "vitamin_d": get_nutrient('Vitamin D (D2 + D3)'),
                "vitamin_c": get_nutrient('Vitamin C, total ascorbic acid'),
                
                # Minerals
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