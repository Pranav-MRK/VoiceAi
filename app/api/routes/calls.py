
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db
from app.memory.manager import MemoryManager
from app.memory.models import Call
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

    messages = await memory.get_conversation(
        db=db,
        call_id=call_id,
    )

    return {
        "call_id": call_id,
        "status": call.status,
        "messages": messages,
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
