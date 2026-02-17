"""
VidyaSetu AI - Challenge Fallbacks
Pre-baked educational challenges for when the LLM is slow or API keys are missing.
"""

FALLBACK_CHALLENGES = {
    "Math": [
        {
            "question": "If Viddy has 12 apples and gives 4 to a friend, how many does he have left?",
            "options": ["6", "8", "10", "12"],
            "correct": "8",
            "explanation": "12 minus 4 is 8! Great subtracting!",
            "trait": "math"
        },
        {
            "question": "What is 5 groups of 3 stars?",
            "options": ["8", "12", "15", "20"],
            "correct": "15",
            "explanation": "5 x 3 = 15. You are reaching for the stars!",
            "trait": "math"
        }
    ],
    "Science": [
        {
            "question": "Which of these is a source of light?",
            "options": ["The Moon", "The Sun", "A Mirror", "A Wall"],
            "correct": "The Sun",
            "explanation": "The Sun is our biggest star and gives us light!",
            "trait": "logical_reasoning"
        },
        {
            "question": "What do plants need most to grow?",
            "options": ["Chocolate", "Ice Cream", "Sunlight & Water", "Toys"],
            "correct": "Sunlight & Water",
            "explanation": "Plants need sun and water to make their own food!",
            "trait": "logical_reasoning"
        }
    ],
    "English": [
        {
            "question": "Which word is an action word (verb)?",
            "options": ["Apple", "Quickly", "Run", "Blue"],
            "correct": "Run",
            "explanation": "'Run' is something you do! That's a verb.",
            "trait": "pattern_recognition"
        }
    ],
    "iq": [
        {
            "question": "Look at the pattern: 2, 4, 6, 8, ... What comes next?",
            "options": ["9", "10", "11", "12"],
            "correct": "10",
            "explanation": "We are counting by 2s! 8 + 2 = 10.",
            "trait": "pattern_recognition"
        }
    ],
    "eq": [
        {
            "question": "Your friend looks sad because they lost their toy. What should you do?",
            "options": ["Laugh at them", "Ignore them", "Ask if they want a hug", "Take their other toys"],
            "correct": "Ask if they want a hug",
            "explanation": "Being kind to friends makes the world better!",
            "trait": "empathy"
        }
    ]
}

def get_random_fallback(subject="GK", category="iq"):
    import random
    
    # Try selection based on subject first
    pool = FALLBACK_CHALLENGES.get(subject, [])
    
    # If subject pool is empty or random chance, use category pool
    if not pool or random.random() > 0.5:
        pool = FALLBACK_CHALLENGES.get(category, FALLBACK_CHALLENGES["iq"])
        
    return random.choice(pool)
