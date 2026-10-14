from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_db
from backend.services import live_notes as svc

class SessionIn(BaseModel):
    title: str = Field(min_length=2)

class TextIn(BaseModel):
    text: str = Field(min_length=2)
    author: str = "scribe"

router = APIRouter()

@router.get("/sessions")
async def sessions(db: AsyncSession = Depends(get_db)):
    rows = await svc.list_sessions(db)
    return {"sessions": [{"id": s.id, "title": s.title, "status": s.status} for s in rows]}

@router.post("/sessions")
async def create(payload: SessionIn, db: AsyncSession = Depends(get_db)):
    s = await svc.start(db, payload.title)
    return {"id": s.id}

@router.post("/sessions/{session_id}/bullets")
async def bullet(session_id: str, payload: TextIn, db: AsyncSession = Depends(get_db)):
    b = await svc.add_bullet(db, session_id, payload.text, payload.author)
    return {"id": b.id}

@router.post("/sessions/{session_id}/decisions")
async def decision(session_id: str, payload: TextIn, db: AsyncSession = Depends(get_db)):
    d = await svc.add_decision(db, session_id, payload.text)
    return {"id": d.id}

@router.get("/sessions/{session_id}")
async def detail(session_id: str, db: AsyncSession = Depends(get_db)):
    s = await db.get(__import__("backend.models", fromlist=["LiveSession"]).LiveSession, session_id)
    if not s:
        raise HTTPException(404, "not found")
    return {
        "id": s.id,
        "title": s.title,
        "summary": s.summary,
        "bullets": [{"id": b.id, "text": b.text, "author": b.author} for b in await svc.bullets(db, session_id)],
        "decisions": [{"id": d.id, "text": d.text} for d in await svc.decisions(db, session_id)],
    }

@router.post("/sessions/{session_id}/summarize")
async def summarize(session_id: str, db: AsyncSession = Depends(get_db)):
    try:
        summary = await svc.summarize(db, session_id)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
    return {"summary": summary}
