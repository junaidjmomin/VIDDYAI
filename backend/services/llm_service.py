import os
from groq import Groq


def generate_key_points(concept: str, grade: int, subject: str):
    """
    Generate simple classroom key points using Groq LLM
    """

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY not configured")

    client = Groq(api_key=api_key)

    prompt = f"""
    Generate 5 short, simple teaching key points for:
    Subject: {subject}
    Concept: {concept}
    Grade: {grade}

    Keep sentences short.
    No numbering.
    One point per line.
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )

    content = response.choices[0].message.content

    points = [
        line.strip("-• ").strip()
        for line in content.split("\n")
        if line.strip()
    ]

    return points[:6]