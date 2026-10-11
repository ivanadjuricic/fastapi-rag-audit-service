"""KORAK 4 - AUDIT: svako pitanje i odgovor se upisuje u log. SELVO naglasava 'full audit trail'."""
import json
import time
from pathlib import Path

LOG = Path("data/audit.jsonl") # primer za env varijablu:LOG = Path(os.getenv("AUDIT_LOG", "data/audit.jsonl")) # za Docker i Docker Compose u profesionalnom radnom okruzenju bi se ovo promenilo


def log_event(user: str, question: str, sources: list[dict]) -> None:
    LOG.parent.mkdir(exist_ok=True)
    event = {
        "time": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "user": user,
        "question": question,
        "sources": [{"source": s["source"], "row": s["row"]} for s in sources],
    }
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
