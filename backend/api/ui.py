from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_db
from backend.models import LiveSession
from backend.services import live_notes as svc

router = APIRouter()
templates = Jinja2Templates(directory="backend/templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, session_id: str | None = None, db: AsyncSession = Depends(get_db)):
    sessions = await svc.list_sessions(db)
    sid = session_id or (sessions[0].id if sessions else None)
    s = await db.get(LiveSession, sid) if sid else None
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Live Meeting Notes",
            "sessions": sessions,
            "session_id": sid,
            "session": s,
            "bullets": await svc.bullets(db, sid) if sid else [],
            "decisions": await svc.decisions(db, sid) if sid else [],
        },
    )

@router.post("/ui/sessions")
async def ui_start(title: str = Form(...), db: AsyncSession = Depends(get_db)):
    s = await svc.start(db, title)
    return RedirectResponse(f"/?session_id={s.id}", status_code=303)

@router.post("/ui/bullets")
async def ui_b(session_id: str = Form(...), text: str = Form(...), db: AsyncSession = Depends(get_db)):
    await svc.add_bullet(db, session_id, text)
    return RedirectResponse(f"/?session_id={session_id}", status_code=303)

@router.post("/ui/decisions")
async def ui_d(session_id: str = Form(...), text: str = Form(...), db: AsyncSession = Depends(get_db)):
    await svc.add_decision(db, session_id, text)
    return RedirectResponse(f"/?session_id={session_id}", status_code=303)

@router.post("/ui/summarize")
async def ui_sum(session_id: str = Form(...), db: AsyncSession = Depends(get_db)):
    await svc.summarize(db, session_id)
    return RedirectResponse(f"/?session_id={session_id}", status_code=303)
