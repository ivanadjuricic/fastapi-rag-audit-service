"""KORAK 2 - RETRIEVAL: nadji najrelevantnije chunk-ove za pitanje.
Koristimo TF-IDF (scikit-learn): radi 100% lokalno, bez interneta - bitno za 'on-premise'.
Kasnija nadogradnja: zameniti TF-IDF pravim embeddings modelom + vektorskom bazom."""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class Index:
    def __init__(self, chunks: list[dict]):
        self.chunks = chunks
        self.vectorizer = TfidfVectorizer(lowercase=True)
        self.matrix = self.vectorizer.fit_transform([c["text"] for c in chunks])

    def search(self, question: str, top_k: int = 5) -> list[dict]:
        scores = cosine_similarity(self.vectorizer.transform([question]), self.matrix).ravel()
        best = scores.argsort()[::-1][:top_k]
        return [{**self.chunks[i], "score": round(float(scores[i]), 3)} for i in best if scores[i] > 0]
