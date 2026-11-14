
import logging
from uuid import uuid4

from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    RunContext,
    function_tool,
)
from livekit.plugins import groq, openai, silero

from app.core.config import settings
from app.db.postgres import AsyncSessionLocal
from app.memory.manager import MemoryManager


logger = logging.getLogger("samvadai.voice")

server = AgentServer()
memory_manager = MemoryManager()


class SamvadAIAgent(Agent):

    def __init__(self, call_id: str, language: str = "en"):
        self.call_id = call_id
        self.language = language

        super().__init__(
            instructions=(
                "You are SamvadAI, a multilingual college admission "
                "assistant.\n"
                "Use the answer_admission_question tool for all "
                "admission-related questions.\n"
                "Do not invent admission information.\n"
                "Speak naturally and keep responses concise, as this "
                "is a phone conversation.\n"
                "If the tool cannot find an answer, explain that "
                "the information is unavailable."
            )
        )

    @function_tool
    async def answer_admission_question(
        self,
        context: RunContext,
        question: str,
    ) -> str:
        """Answer a caller's college admission question using SamvadAI's RAG knowledge base.

        Args:
            question: The caller's admission-related question.
        """

        logger.info("Processing voice question for call %s", self.call_id)
        from app.memory.conversation import process_message
        async with AsyncSessionLocal() as db:
            result = await process_message(
                db=db,
                call_id=self.call_id,
                query=question,
                language=self.language,
            )

        return result["answer"]


@server.rtc_session(agent_name="samvadai-voice-agent")
async def entrypoint(ctx: JobContext):

    call_id = str(uuid4())
    language = "en"

    logger.info(
        "Starting SamvadAI voice call: %s",
        call_id,
    )

    # Create persistent call record.
    async with AsyncSessionLocal() as db:
        await memory_manager.start_call(
            db=db,
            call_id=call_id,
            language=language,
        )

    # Close the call and clear temporary memory when the session ends.
    async def cleanup():
        logger.info("Ending SamvadAI call: %s", call_id)

        async with AsyncSessionLocal() as db:
            await memory_manager.end_call(
                db=db,
                call_id=call_id,
            )

    ctx.add_shutdown_callback(cleanup)

    # Configure speech processing.
    session = AgentSession(
        stt=groq.STT(
            model="whisper-large-v3-turbo",
            language=language,
        ),
        llm=groq.LLM(
            model=settings.GROQ_MODEL,
            temperature=0,
        ),
        tts=openai.TTS(
            model="kokoro",
            voice="af_bella",
            api_key="not-needed",
            base_url="http://localhost:8880/v1",
            response_format="wav",
        ),
        vad=silero.VAD.load(),
    )

    await session.start(
        agent=SamvadAIAgent(
            call_id=call_id,
            language=language,
        ),
        room=ctx.room,
    )
    await ctx.connect()

    await session.generate_reply(
        instructions=(
            "Greet the caller as SamvadAI. "
            "Tell them you can help with college admission questions."
        )
    )


if __name__ == "__main__":
    from livekit.agents import cli

    cli.run_app(server)
