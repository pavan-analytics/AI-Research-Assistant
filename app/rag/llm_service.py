import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


class LLMService:

    def generate_answer(self, question, context):

        prompt = f"""
You are an AI Research Assistant.

Answer ONLY using the provided context.

If the answer is not available in the context, reply exactly:

"I couldn't find this information in the uploaded documents."

Context:
{context}

Question:
{question}
"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2
        )

        return response.choices[0].message.content