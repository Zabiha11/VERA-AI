
import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

# Find the project root and load its .env file
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

API_KEY = os.getenv("GROQ_API_KEY")
MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

if not API_KEY:
    raise ValueError(
        "GROQ_API_KEY is missing. Add it to the project's .env file."
    )

# Create the Groq client
client = Groq(api_key=API_KEY)


def ask_groq(user_message):
    """Send a message to Groq and return its response."""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are VERA, a helpful AI personal desktop assistant. "
                    "Understand natural language, answer clearly, and "
                    "help the user accomplish tasks. Do not claim to have "
                    "performed an action unless a tool has actually done it."
                )
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        temperature=0.3,
        max_completion_tokens=500
    )

    return response.choices[0].message.content
