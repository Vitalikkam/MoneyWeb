"""
Emoji fallback for vocabulary words when images aren't available.
"""

EMOJI_MAP = {
    # Feelings
    "happy": "😊",
    "sad": "😢",
    "angry": "😡",
    "fear": "😨",
    "love": "❤️",
    "surprise": "😮",
    "excited": "🤩",
    "tired": "😫",
    "peaceful": "😌",
    "anxious": "😰",
    "calm": "😌",
    "joy": "🥳",
    "grief": "😭",
    "hope": "🙏",
    
    # Nature
    "sun": "☀️",
    "moon": "🌙",
    "rain": "🌧️",
    "snow": "❄️",
    "tree": "🌳",
    "flower": "🌸",
    "animal": "🐾",
    "elephant": "🐘",
    "lion": "🦁",
    "tiger": "🐯",
    "dog": "🐕",
    "cat": "🐈",
    "bird": "🐦",
    "fish": "🐟",
    "forest": "🌲",
    "ocean": "🌊",
    "mountain": "⛰️",
    "star": "⭐",
    "fire": "🔥",
    "water": "💧",
    
    # Food
    "apple": "🍎",
    "bread": "🍞",
    "cake": "🎂",
    "coffee": "☕",
    "water": "💧",
    "pizza": "🍕",
    "ice_cream": "🍦",
    "chocolate": "🍫",
    "fruit": "🍉",
    "vegetable": "🥬",
    "meat": "🥩",
    "cheese": "🧀",
    "wine": "🍷",
    
    # Objects
    "book": "📚",
    "house": "🏠",
    "car": "🚗",
    "phone": "📱",
    "computer": "💻",
    "money": "💰",
    "heart": "💖",
    "fire": "🔥",
    "light": "💡",
    "key": "🔑",
    "clock": "⏰",
    "bell": "🔔",
    "tool": "🔧",
    "machine": "⚙️",
    "building": "🏢",
    "bridge": "🌉",
    "road": "🛣️",
    
    # Actions
    "run": "🏃",
    "walk": "🚶",
    "eat": "🍽️",
    "drink": "🥤",
    "sleep": "😴",
    "read": "📖",
    "write": "✍️",
    "speak": "🗣️",
    "listen": "👂",
    "see": "👁️",
    "think": "🤔",
    "work": "💼",
    "play": "🎮",
    "travel": "✈️",
    "swim": "🏊",
    "fly": "🛫",
    
    # Abstract
    "time": "⏳",
    "life": "🌱",
    "death": "⚰️",
    "dream": "💭",
    "idea": "💡",
    "truth": "✅",
    "lie": "❌",
    "beauty": "🌸",
    "ugly": "👹",
    "strong": "💪",
    "weak": "🫤",
    "fast": "🏎️",
    "slow": "🐢",
    
    # People
    "man": "👨",
    "woman": "👩",
    "child": "🧒",
    "friend": "🤝",
    "family": "👨‍👩‍👧‍👦",
    "enemy": "👤",
    "teacher": "👨‍🏫",
    "student": "🧑‍🎓",
    "doctor": "👨‍⚕️",
    "artist": "🎨",
    "musician": "🎵",
}

def get_emoji(word):
    """Get emoji for a word if available."""
    if not word:
        return None
    
    word_lower = word.lower().strip()
    
    # Try exact match first
    if word_lower in EMOJI_MAP:
        return EMOJI_MAP[word_lower]
    
    # Try partial match
    for key, emoji in EMOJI_MAP.items():
        if key in word_lower or word_lower in key:
            return emoji
    
    return None