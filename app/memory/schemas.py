
from datetime import datetime
from pydantic import BaseModel, Field


class MessageSchema(BaseModel):
    role: str = Field(
        pattern="^(user|assistant)$"
    )

    content: str = Field(min_length=1)

    timestamp: datetime | None = None


class ConversationSchema(BaseModel):
    call_id: str

    messages: list[MessageSchema] = []

    language: str = "en"
