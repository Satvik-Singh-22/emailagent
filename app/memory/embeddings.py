from dotenv import load_dotenv
from app.llm.gemini import client

load_dotenv()


def embed_text(text: str) -> list[float]:
    """
    Convert text into a 768-dim embedding vector using Gemini.
    """

    if not text or not text.strip():
        raise ValueError("Cannot embed empty text")

    response = client.models.embed_content(
        model="models/text-embedding-004",
        contents=text
    )

    # ✅ Correct for your SDK version
    embedding = response.embeddings[0].values

    if len(embedding) != 768:
        raise ValueError(f"Expected 768-dim embedding, got {len(embedding)}")

    return embedding
