from fastapi import Query, Body , APIRouter
from bson import ObjectId
from  database import db, serialize
from datetime import datetime, timezone

router = APIRouter(prefix="/rooms", tags=["messages"])

@router.get("/{room}/messages")
async def get_messages(
    room: str,
    limit: int = Query(20, ge=1, le=100),
    before_id: str | None = Query(None),
):
    query = {"room": room}
    if before_id:
        try:
            query["_id"] = {"$lt": ObjectId(before_id)}
        except Exception:
            pass

    cursor = db()["messages"].find(query).sort("_id", -1).limit(limit)
    docs = [serialize(d) async for d in cursor]
    docs.reverse()
    next_cursor = docs[0]["_id"] if docs else None
    return {"items": docs, "next_cursor": next_cursor}


@router.post("/{room}/messages", status_code=201)
async def post_message(
    room: str,
    username: str = Body(..., embed=True),
    content: str = Body(..., embed=True),
):
    doc = {
        "room": room,
        "username": username[:50],
        "content": content[:1000],
        "created_at": datetime.now(timezone.utc),
    }
    res = await db()["messages"].insert_one(doc)
    doc["_id"] = res.inserted_id
    return serialize(doc)