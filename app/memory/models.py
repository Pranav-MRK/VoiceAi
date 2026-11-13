
import uuid

from datetime import datetime, timezone

from sqlalchemy import (
    String,
    Text,
    DateTime,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.postgres import Base


class Call(Base):
    __tablename__ = "calls"

    call_id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
    )

    language: Mapped[str] = mapped_column(
        String(20),
        default="en",
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="active",
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    messages: Mapped[list["ConversationMessage"]] = relationship(
        back_populates="call",
        cascade="all, delete-orphan",
    )


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    call_id: Mapped[str] = mapped_column(
        ForeignKey("calls.call_id", ondelete="CASCADE"),
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    call: Mapped["Call"] = relationship(
        back_populates="messages",
    )


Index(
    "idx_messages_call_created",
    ConversationMessage.call_id,
    ConversationMessage.created_at,
)
