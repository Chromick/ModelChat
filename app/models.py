# app/models.py
from pydantic import BaseModel, Field
from datetime import datetime, timezone

# --- Schemas Pydantic ---
class MessageIn(BaseModel):
    username: str = Field(..., max_length=50, description="Nome do usuário")
    content: str = Field(..., max_length=1000, description="Conteúdo da mensagem")

class MessageOut(BaseModel):
    _id: str
    room: str
    username: str
    content: str
    created_at: datetime

# --- Funções de serialização ---
def iso(dt: datetime) -> str:
    """Converte datetime em string ISO 8601 com timezone."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()

def serialize(doc: dict) -> dict:
    """Serializa documentos do MongoDB para JSON."""
    d = dict(doc)
    if "_id" in d:
        d["_id"] = str(d["_id"])
    if "created_at" in d and isinstance(d["created_at"], datetime):
        d["created_at"] = iso(d["created_at"])
    return d
