
import asyncio

from livekit.plugins import groq
from app.core.config import settings


async def main():
    api_key = settings.GROQ_API_KEY
    if api_key is None:
        raise ValueError("GROQ_API_KEY is not configured")

    stt = groq.STT(
        model="whisper-large-v3-turbo",
        api_key=api_key,
    )

    print("Groq STT initialized successfully!")
    print("Model: whisper-large-v3-turbo")


if __name__ == "__main__":
    asyncio.run(main())
