from fastapi import APIRouter, Query, HTTPException
from bson import ObjectId
from datetime import datetime, timezone
from typing import Optional

from app.database import db
from app.models import MessageIn, MessageOut, serialize

router = APIRouter(prefix="/rooms", tags=["messages"])

# --- GET: listar mensagens ---
@router.get("/{room}/messages")
async def get_messages(
    room: str,
    limit: int = Query(20, ge=1, le=100),
    before_id: Optional[str] = Query(None),
):
    query = {"room": room}
    if before_id:
        try:
            query["_id"] = {"$lt": ObjectId(before_id)}
        except Exception:
            raise HTTPException(status_code=400, detail="before_id inválido")

    cursor = db()["messages"].find(query).sort("_id", -1).limit(limit)
    docs = [serialize(d) async for d in cursor]
    docs.reverse()
    next_cursor = docs[0]["_id"] if docs else None
    return {"items": docs, "next_cursor": next_cursor}

# --- POST: enviar mensagem ---
@router.post("/{room}/messages", response_model=MessageOut, status_code=201)
async def post_message(room: str, message: MessageIn):
    if not message.content.strip():
        raise HTTPException(status_code=400, detail="Mensagem não pode ser vazia")

    doc = {
        "room": room,
        "username": message.username,
        "content": message.content,
        "created_at": datetime.now(timezone.utc),
    }
    res = await db()["messages"].insert_one(doc)
    doc["_id"] = str(res.inserted_id)
    return serialize(doc)
