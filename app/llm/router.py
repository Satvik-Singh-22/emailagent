from app.llm.gemini import call_gemini
from app.llm.ollama import call_ollama
from google.genai.errors import ClientError


def call_llm(prompt: str, task: str) -> str:
    try:
        return call_gemini(prompt)
    except ClientError as e:
        # Quota / rate limit / API errors
        print(f"⚠️ Gemini failed ({task}):", e)
        return call_ollama(prompt)
    except Exception as e:
        print(f"⚠️ LLM error ({task}):", e)
        return call_ollama(prompt)
