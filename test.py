from app.memory.embeddings import embed_text

text = "User composed a short informal email to a college peer."

embedding = embed_text(text)

print(type(embedding))
print(len(embedding))
print(embedding[:5])  # just to see numbers
