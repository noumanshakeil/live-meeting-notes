from __future__ import annotations
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.llm import get_llm
from backend.models import Decision, LiveSession, NoteBullet

async def start(session: AsyncSession, title: str) -> LiveSession:
    row = LiveSession(id=uuid.uuid4().hex[:10], title=title.strip()[:200])
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return row

async def list_sessions(session: AsyncSession) -> list[LiveSession]:
    return list((await session.execute(select(LiveSession).order_by(LiveSession.created_at.desc()))).scalars())

async def add_bullet(session: AsyncSession, session_id: str, text: str, author: str = "scribe") -> NoteBullet:
    b = NoteBullet(id=uuid.uuid4().hex[:10], session_id=session_id, text=text.strip(), author=author[:80])
    session.add(b)
    await session.commit()
    await session.refresh(b)
    return b

async def add_decision(session: AsyncSession, session_id: str, text: str) -> Decision:
    drow = Decision(id=uuid.uuid4().hex[:10], session_id=session_id, text=text.strip())
    session.add(drow)
    await session.commit()
    await session.refresh(drow)
    return drow

async def bullets(session: AsyncSession, session_id: str) -> list[NoteBullet]:
    return list((await session.execute(select(NoteBullet).where(NoteBullet.session_id == session_id))).scalars())

async def decisions(session: AsyncSession, session_id: str) -> list[Decision]:
    return list((await session.execute(select(Decision).where(Decision.session_id == session_id))).scalars())

async def summarize(session: AsyncSession, session_id: str) -> str:
    row = await session.get(LiveSession, session_id)
    if not row:
        raise ValueError("not found")
    notes = await bullets(session, session_id)
    decs = await decisions(session, session_id)
    blob = "NOTES:\n" + "\n".join(f"- {n.text}" for n in notes)
    blob += "\nDECISIONS:\n" + "\n".join(f"- {d.text}" for d in decs)
    llm = get_llm()
    summary = await llm.complete(blob, system="Write a rolling meeting summary with decisions called out.")
    row.summary = summary
    await session.commit()
    return summary
