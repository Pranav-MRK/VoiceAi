
from contextlib import asynccontextmanager
from app.api.routes.calls import router as calls_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.dashboard import router as dashboard_router
from app.db.postgres import close_postgres
from app.db.redis import get_redis, close_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Verify database connections on startup
    redis = await get_redis()
    await redis.ping()

    # Application is ready
    yield

    # Close connections on shutdown
    await close_redis()
    await close_postgres()

app = FastAPI(
    title="SamvadAI API",
    description="Multilingual AI-powered college admission voice assistant",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(calls_router)
app.include_router(dashboard_router)

# CORS configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "Welcome to SamvadAI API",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "SamvadAI",
    }
