
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.postgres import get_db
from app.memory.manager import MemoryManager
from app.memory.models import Call, ConversationMessage
from app.memory.conversation import process_message
import logging

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/api/calls", tags=["Calls"])

memory = MemoryManager()


# Request schemas
class StartCallRequest(BaseModel):
    language: str = "en"


class MessageRequest(BaseModel):
    message: str = Field(min_length=1, max_length=5000)



@router.get("")
async def list_calls(
    limit: int = 10,
    offset: int = 0,
    status: str | None = None,
    language: str | None = None,
    search: str | None = None,
    sort: str = "newest",
    db: AsyncSession = Depends(get_db),
):
    limit = max(1, min(limit, 100))
    offset = max(0, offset)

    query = select(Call)

    if status in ("active", "completed"):
        query = query.where(Call.status == status)

    if language:
        query = query.where(Call.language == language)

    if search and search.strip():
        query = query.where(
            Call.call_id.ilike(f"%{search.strip()}%")
        )

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.scalar(count_query)
    total = total_result or 0

    order_column = (
        Call.started_at.asc()
        if sort == "oldest"
        else Call.started_at.desc()
    )

    message_count = (
        select(func.count(ConversationMessage.id))
        .where(ConversationMessage.call_id == Call.call_id)
        .scalar_subquery()
    )

    result = await db.execute(
        select(Call, message_count.label("message_count"))
        .where(
            Call.call_id.in_(
                query.with_only_columns(Call.call_id)
            )
        )
        .order_by(order_column)
        .offset(offset)
        .limit(limit)
    )

    rows = result.all()

    return {
        "calls": [
            {
                "call_id": call.call_id,
                "language": call.language,
                "status": call.status,
                "started_at": call.started_at,
                "ended_at": call.ended_at,
                "message_count": count,
            }
            for call, count in rows
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }



# 1. Start a new call
@router.post("/start")
async def start_call(
    request: StartCallRequest,
    db: AsyncSession = Depends(get_db),
):
    call_id = str(uuid4())

    await memory.start_call(
        db=db,
        call_id=call_id,
        language=request.language,
    )

    return {
        "call_id": call_id,
        "status": "active",
        "language": request.language,
    }


# 2. Send a message and receive an AI response
@router.post("/{call_id}/message")
async def send_message(
    call_id: str,
    request: MessageRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Call).where(Call.call_id == call_id)
    )
    call = result.scalar_one_or_none()

    if call is None:
        raise HTTPException(
            status_code=404,
            detail="Call not found",
        )

    if call.status != "active":
        raise HTTPException(
            status_code=400,
            detail="This call has already ended",
        )

    try:
        result = await process_message(
            db=db,
            call_id=call_id,
            query=request.message.strip(),
            language=call.language,
        )
        return result

    except Exception:
        logger.exception("Failed to process message for call_id=%s", call_id)

        raise HTTPException(
            status_code=500,
            detail="Failed to process the message",
        )


# 3. Retrieve conversation history

@router.get("/{call_id}/history")
async def get_call_history(
    call_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Call).where(Call.call_id == call_id)
    )
    call = result.scalar_one_or_none()

    if call is None:
        raise HTTPException(
            status_code=404,
            detail="Call not found",
        )

    result = await db.execute(
        select(ConversationMessage)
        .where(ConversationMessage.call_id == call_id)
        .order_by(ConversationMessage.created_at.asc())
    )

    messages = result.scalars().all()

    return {
        "call_id": call_id,
        "status": call.status,
        "language": call.language,
        "started_at": call.started_at,
        "ended_at": call.ended_at,
        "messages": [
            {
                "role": message.role,
                "content": message.content,
                "timestamp": message.created_at,
            }
            for message in messages
        ],
    }



# 4. End a call
@router.post("/{call_id}/end")
async def end_call(
    call_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Call).where(Call.call_id == call_id)
    )
    call = result.scalar_one_or_none()

    if call is None:
        raise HTTPException(
            status_code=404,
            detail="Call not found",
        )

    if call.status == "completed":
        return {
            "call_id": call_id,
            "status": "completed",
            "message": "Call has already ended",
        }

    await memory.end_call(
        db=db,
        call_id=call_id,
    )

    return {
        "call_id": call_id,
        "status": "completed",
        "message": "Call ended successfully",
    }
