
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db
from app.memory.models import Call, ConversationMessage

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
):
    total_calls = await db.scalar(
        select(func.count()).select_from(Call)
    )

    active_calls = await db.scalar(
        select(func.count())
        .select_from(Call)
        .where(Call.status == "active")
    )

    completed_calls = await db.scalar(
        select(func.count())
        .select_from(Call)
        .where(Call.status == "completed")
    )

    total_messages = await db.scalar(
        select(func.count()).select_from(ConversationMessage)
    )

    return {
        "total_calls": total_calls or 0,
        "active_calls": active_calls or 0,
        "completed_calls": completed_calls or 0,
        "total_messages": total_messages or 0,
    }


@router.get("/analytics")
async def get_dashboard_analytics(
    db: AsyncSession = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=6)

    # Daily call activity for the last 7 days.
    daily_date = func.date(Call.started_at)

    daily_query = (
        select(
            daily_date.label("day"),
            func.count(Call.call_id).label("total"),
            func.sum(
                case((Call.status == "completed", 1), else_=0)
            ).label("completed"),
            func.sum(
                case((Call.status == "active", 1), else_=0)
            ).label("active"),
        )
        .where(Call.started_at >= start_date)
        .group_by(daily_date)
        .order_by(daily_date)
    )

    daily_result = await db.execute(daily_query)
    daily_rows = daily_result.all()

    daily_lookup = {
        row.day: {
            "total_calls": row.total,
            "completed_calls": row.completed,
            "active_calls": row.active,
        }
        for row in daily_rows
    }

    daily_activity = []

    for day_offset in range(7):
        day = (start_date + timedelta(days=day_offset)).date()
        values = daily_lookup.get(
            day,
            {
                "total_calls": 0,
                "completed_calls": 0,
                "active_calls": 0,
            },
        )

        daily_activity.append({
            "date": day.isoformat(),
            **values,
        })

    # Lifetime call status distribution.
    status_result = await db.execute(
        select(Call.status, func.count(Call.call_id))
        .group_by(Call.status)
    )

    call_status = [
        {"status": status, "count": count}
        for status, count in status_result.all()
    ]

    # Lifetime language distribution.
    language_result = await db.execute(
        select(Call.language, func.count(Call.call_id))
        .group_by(Call.language)
        .order_by(func.count(Call.call_id).desc())
    )

    language_distribution = [
        {"language": language, "count": count}
        for language, count in language_result.all()
    ]

    # Total messages.
    total_messages = await db.scalar(
        select(func.count()).select_from(ConversationMessage)
    )

    # Average duration of completed calls.
    duration_seconds = func.extract(
        "epoch",
        Call.ended_at - Call.started_at,
    )

    average_duration = await db.scalar(
        select(func.avg(duration_seconds))
        .where(
            Call.status == "completed",
            Call.ended_at.is_not(None),
        )
    )

    return {
        "period": "last_7_days",
        "daily_activity": daily_activity,
        "call_status": call_status,
        "language_distribution": language_distribution,
        "total_messages": total_messages or 0,
        "average_call_duration_seconds": round(
            float(average_duration or 0), 2
        ),
    }
