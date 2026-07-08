"""
Supplements configuration – your supplement list and defaults.
"""

DEFAULT_SUPPLEMENTS = [
    {"name": "Creatine", "dosage": 5, "unit": "g"},
    {"name": "L-Tyrosine", "dosage": 500, "unit": "mg"},
    {"name": "L-Theanine", "dosage": 200, "unit": "mg"},
    {"name": "Ashwagandha", "dosage": 900, "unit": "mg"},
    {"name": "Tongkat Ali", "dosage": 500, "unit": "mg"},
    {"name": "Fadogia Agrestis", "dosage": 450, "unit": "mg"},
    {"name": "Omega-3", "dosage": 6000, "unit": "mg"},
    {"name": "Magnesium", "dosage": 240, "unit": "mg"},
    {"name": "Zinc", "dosage": 15, "unit": "mg"},
    {"name": "Vitamin B6", "dosage": 2.8, "unit": "mg"},
    {"name": "Vitamin D3", "dosage": 100, "unit": "µg"},
]

def get_supplement_config():
    """Get the supplement configuration."""
    return DEFAULT_SUPPLEMENTS

def get_supplement_names():
    """Get list of supplement names."""
    return [s["name"] for s in DEFAULT_SUPPLEMENTS]

def get_supplement_dosage(name):
    """Get dosage for a supplement by name."""
    for s in DEFAULT_SUPPLEMENTS:
        if s["name"] == name:
            return f"{s['dosage']} {s['unit']}"
    return ""