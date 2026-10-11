"""KORAK 1 - INGEST: ucitaj Excel/CSV, napravi profil kvaliteta podataka i iseci tabelu na 'chunk-ove'."""
import pandas as pd


def load_table(path: str) -> pd.DataFrame:
    if path.lower().endswith(".csv"):
        return pd.read_csv(path)
    return pd.read_excel(path)


def profile(df: pd.DataFrame) -> dict:
    """Slicno onome sto SELVO prikazuje: broj redova, kolone, procenat praznih polja."""
    missing = (df.isna().mean() * 100).round(1)
    return {
        "rows": int(len(df)),
        "columns": list(df.columns),
        "missing_percent": {c: float(v) for c, v in missing.items() if v > 0},
    }


def make_chunks(df: pd.DataFrame, filename: str) -> list[dict]:
    """Jedan chunk = jedan red tabele, pretvoren u tekst. Cuvamo ODAKLE potice (izvor)."""
    chunks = []
    for i, row in df.iterrows():
        text = " | ".join(f"{col}: {val}" for col, val in row.items() if pd.notna(val))
        chunks.append({"source": filename, "row": int(i) + 2, "text": text})  # +2 = red u Excel-u (zaglavlje je red 1)
    return chunks
