"""
VidyaSetu AI — Validator Service
Ensures uploaded PDFs + questions are safe, grade-appropriate,
and match selected subject.
"""

from typing import Tuple, List

# ───────────────── CONFIG ─────────────────

FORBIDDEN_KEYWORDS_PDF = [
    "machine learning","neural network","deep learning","artificial intelligence",
    "tensor","regression","classification","clustering","reinforcement learning",
    "phd","thesis","dissertation","journal","ieee","acm","arxiv",
    "tensorflow","pytorch","keras","university","semester",
    "engineering","medical","finance","business administration",
    "pornography","sexual","drug","alcohol","tobacco"
]

# Categorized question filtering
FORBIDDEN_KEYWORDS_QUESTION = {
    "violence": ["kill","murder","bomb","attack","weapon","suicide"],
    "adult": ["porn","xxx","sex","nude"],
    "drugs": ["cocaine","heroin","meth","weed","drug"],
    "prompt": ["ignore previous instructions","system prompt","jailbreak"],
    "offtopic": ["movie","cinema","celebrity","gossip","casino","bitcoin","crypto"]
}

SAFETY_RESPONSES = {
    "violence":
        "I can’t help with harmful or violent topics.\n\n"
        "Let’s learn something safe from your textbook instead.",

    "adult":
        "That topic isn’t appropriate for our learning space.\n\n"
        "Ask me something from your subject and I’ll help you learn! 📚",

    "drugs":
        "I can’t help with harmful substances.\n\n"
        "If you like chemistry, we can explore safe experiments instead.",

    "prompt":
        "I must follow safe learning rules 🙂\n\n"
        "Ask me any academic question!",

    "offtopic":
        "That sounds fun, but I'm here to help with studies.\n\n"
        "Ask something from your textbook!"
}

SUBJECT_KEYWORDS = {
    "math": [
        "number","addition","subtraction","multiplication","division",
        "fraction","decimal","geometry","angle","measurement"
    ],

    "science": [
        "plant","animal","energy","force","experiment","body",
        "environment","water","air","food chain"
    ],

    "english": [
        "grammar","noun","verb","adjective","sentence","story",
        "reading","writing","spelling","paragraph"
    ],

    "hindi": [
        "हिंदी","व्याकरण","कविता","कहानी","संज्ञा","क्रिया","शब्द"
    ],

    "social": [
        "history","geography","map","earth","india","river","mountain"
    ],

    "general": []
}

# minimum subject relevance
MIN_SUBJECT_MATCH = 5


# ───────────────── HELPERS ─────────────────

def _count_matches(text: str, keywords: List[str]) -> int:
    text = text.lower()
    return sum(text.count(k.lower()) for k in keywords)


def _detect_subject(text: str) -> str:
    scores = {}

    for subject, keywords in SUBJECT_KEYWORDS.items():
        scores[subject] = _count_matches(text, keywords)

    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "general"


# ───────────────── PDF VALIDATOR ─────────────────

def validate_pdf_content(
    extracted_text: str,
    subject: str,
    grade: int
) -> Tuple[bool, str]:

    if not extracted_text or len(extracted_text.strip()) < 200:
        return False, "PDF seems empty or scanned. Upload a readable textbook."

    text = extracted_text.lower()

    # 1️⃣ Block advanced / unsafe content
    forbidden_score = _count_matches(text, FORBIDDEN_KEYWORDS_PDF)
    if forbidden_score >= 3:
        return False, (
            "This document looks like advanced academic material.\n"
            "Please upload a Grade {} {} textbook.".format(grade, subject)
        )

    # 2️⃣ Strict SUBJECT VALIDATION (YOUR MAIN ISSUE)
    subject = subject.lower()

    if subject != "general":

        subject_score = _count_matches(text, SUBJECT_KEYWORDS.get(subject, []))

        detected_subject = _detect_subject(text)

        # Reject if subject relevance too low
        if subject_score < MIN_SUBJECT_MATCH:
            return False, (
                f"This doesn't look like a {subject.capitalize()} textbook.\n"
                f"It seems closer to {detected_subject.capitalize()}.\n"
                "Please upload the correct subject book."
            )

    print("[Validator] PDF accepted")
    return True, "Valid textbook."


# ───────────────── QUESTION VALIDATOR ─────────────────

def validate_question(
    question: str,
    grade: int,
    subject: str
) -> Tuple[bool, str]:

    if not question or len(question.strip()) < 2:
        return False, "Please ask a proper question 🙂"

    q = question.lower()

    # Educational safety refusal
    for category, words in FORBIDDEN_KEYWORDS_QUESTION.items():
        for w in words:
            if w in q:
                print(f"[Validator] Question blocked ({category})")
                return False, SAFETY_RESPONSES[category]

    print("[Validator] Question allowed")
    return True, "Allowed"
