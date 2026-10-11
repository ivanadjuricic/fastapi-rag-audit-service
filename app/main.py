"""KORAK 3 - API: FastAPI endpoint-i. Svaki endpoint je jedna funkcija povezana sa URL-om."""
import io
import os
import shutil

import pandas as pd
from fastapi import FastAPI, File, Header, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.audit import log_event
from app.ingest import load_table, make_chunks, profile
from app.retrieval import Index

app = FastAPI(title="fastapi-rag-audit-service", description="Mali on-premise RAG demo (retrieval + izvori + audit)")

STATE: dict = {"index": None, "df": None, "filename": None}   # cuvamo u memoriji (dovoljno za demo)


class Question(BaseModel):          # Pydantic: FastAPI automatski proverava da zahtev ima polje 'question'
    question: str
    top_k: int = 5


@app.get("/health")
def health():
    return {"status": "online"}


@app.post("/documents")
async def upload_document(file: UploadFile = File(...)):
    """Primi Excel/CSV, napravi profil i indeks."""
    if not file.filename.lower().endswith((".xlsx", ".csv")):
        raise HTTPException(status_code=400, detail="Podrzani su samo .xlsx i .csv")
    os.makedirs("data/uploads", exist_ok=True)
    path = f"data/uploads/{file.filename}"
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    df = load_table(path)
    STATE.update(df=df, filename=file.filename, index=Index(make_chunks(df, file.filename)))
    return {"filename": file.filename, "profile": profile(df)}


@app.post("/ask")
def ask(q: Question, x_user: str = Header(default="anonymous")):
    """Pronadji relevantne redove, vrati ih sa izvorima i upisi u audit log."""
    if STATE["index"] is None:
        raise HTTPException(status_code=409, detail="Prvo ucitaj dokument (POST /documents)")
    hits = STATE["index"].search(q.question, q.top_k)
    log_event(x_user, q.question, hits)
    return {
        "question": q.question,
        "answer": f"Pronadjeno {len(hits)} relevantnih redova u '{STATE['filename']}'.",
        "sources": hits,     # 'traceable' - svaki rezultat ima fajl i broj reda
    }


@app.get("/stats/{column}")
def stats(column: str, group_by: str | None = None):
    """Strukturirana analiza (kao 'average resolution time by priority' u SELVO demou), radi pandas."""
    df: pd.DataFrame | None = STATE["df"]
    if df is None:
        raise HTTPException(status_code=409, detail="Prvo ucitaj dokument")
    if column not in df.columns or (group_by and group_by not in df.columns):
        raise HTTPException(status_code=404, detail=f"Kolone: {list(df.columns)}")
    result = df.groupby(group_by)[column].mean() if group_by else df[column].describe()
    return result.round(2).to_dict()


@app.get("/export")
def export(column: str, group_by: str):
    """Izvezi rezultat analize u Excel (SELVO ima 'Excel export ready')."""
    df = STATE["df"]
    if df is None:
        raise HTTPException(status_code=409, detail="Prvo ucitaj dokument")
    out = df.groupby(group_by)[column].mean().round(2).reset_index()
    buf = io.BytesIO()
    out.to_excel(buf, index=False)
    buf.seek(0)
    return StreamingResponse(buf, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": "attachment; filename=export.xlsx"})
