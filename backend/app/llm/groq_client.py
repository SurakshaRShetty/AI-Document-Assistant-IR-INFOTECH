from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_answer(query: str, context: str) -> str:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a retrieval-augmented question answering system. "
                    "Answer ONLY using the provided context. "
                    "If the answer is not clearly present, say so explicitly. "
                    "Do NOT use outside knowledge."
                )
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion:\n{query}"
            }
        ],
        temperature=0.1,
        max_tokens=300,
    )
    return response.choices[0].message.content.strip()
