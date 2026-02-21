"""
VidyaSetu AI — Validator Service
Educational Safety + Subject Alignment Layer
"""

from typing import Tuple, List, Dict


# ───────────────── PDF SAFETY FILTER ─────────────────

FORBIDDEN_KEYWORDS_PDF = [
    # Advanced Academic Content
    "machine learning","neural network","deep learning","artificial intelligence",
    "tensor","regression","classification","clustering","reinforcement learning",
    "phd","thesis","dissertation","journal","ieee","acm","arxiv",
    "tensorflow","pytorch","keras","university","semester",

    # Professional Domains (not primary school)
    "engineering","medical","finance","business administration","law",

    # Unsafe material
    "pornography","sexual","drug","alcohol","tobacco","violence"
]


# ───────────────── QUESTION SAFETY FILTER ─────────────────

FORBIDDEN_KEYWORDS_QUESTION: Dict[str, List[str]] = {

    # Harm / Violence
    "violence": [
        "kill","murder","bomb","attack","weapon","shoot","suicide","stab", "gun"
    ],

    # Adult content
    "adult": [
        "porn","xxx","sex","nude","onlyfans"
    ],

    # Drugs / substances
    "drugs": [
        "cocaine","heroin","meth","weed","drug","alcohol","smoking"
    ],

    # Prompt attacks / jailbreak attempts
    "prompt": [
        "ignore previous instructions",
        "system prompt",
        "jailbreak",
        "act as",
        "developer mode",
        "unfiltered"
    ],

    # Non-academic distractions
    "offtopic": [
        "movie","cinema","celebrity","gossip",
        "casino","betting","bitcoin","crypto",
        "instagram","tiktok","youtube"
    ],
}


# ───────────────── EDUCATIONAL REDIRECT RESPONSES ─────────────────

SAFETY_RESPONSES = {

    "violence":
        "I can’t help with harmful or dangerous topics.\n\n"
        "Real learning keeps people safe. "
        "Let’s explore something from your textbook instead 📚.",


    "adult":
        "That topic isn’t suitable for a school learning space.\n\n"
        "Ask me anything from your subject and we’ll learn together! 🌱",


    "drugs":
        "I can’t help with harmful substances.\n\n"
        "If you're curious about science, we can explore safe chemistry or biology ideas instead 🔬.",


    "prompt":
        "I follow learning safety rules so students get trustworthy answers 🙂\n\n"
        "Try asking a question from your lesson!",


    "offtopic":
        "That sounds interesting, but I'm your study companion right now.\n\n"
        "Let’s focus on your subject — what chapter are you studying? 📖",
}


# ───────────────── CORE SAFETY CHECK ─────────────────

def detect_forbidden_category(question: str) -> Tuple[bool, str]:
    """
    Detects if question belongs to a forbidden category.

    Returns:
        (is_blocked, response_message)
    """

    if not question:
        return False, ""

    q = question.lower()

    for category, keywords in FORBIDDEN_KEYWORDS_QUESTION.items():
        for kw in keywords:
            if kw in q:
                return True, SAFETY_RESPONSES.get(
                    category,
                    "Let's focus on learning topics instead! 📚"
                )

    return False, ""

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
