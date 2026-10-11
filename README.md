# Mini-SELVO — mali on-premise RAG demo

Pokretanje (bez Dockera):
    python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    python make_sample_data.py
    uvicorn app.main:app --reload
Otvori http://localhost:8000/docs  (FastAPI sam pravi interaktivnu stranicu za testiranje)

Docker:
    docker build -t mini-selvo .
    docker run -p 8000:8000 mini-selvo

Testovi: python -m pytest -q

Tok: Excel -> profil kvaliteta -> chunk (1 red = 1 chunk) -> TF-IDF indeks -> /ask vraca redove + izvor (fajl, red) -> audit log (data/audit.jsonl)
Ograničenja (iskreno): nema LLM-a (samo retrieval), TF-IDF umesto embeddings, stanje u memoriji, nema prave autentifikacije.
Sledeći koraci: embeddings + vektorska baza, lokalni LLM (npr. Ollama) za generisanje odgovora, role-based access.

Projekat kreiran u svrhu učenja i demonstracije RAG koncepta, obrade dokumenata i FastAPI backend integracije za on-premise analitiku.