"""
Cross-Border Payment Intelligence Platform — FastAPI Application.
Thin entry point: creates the app, wires routers, sets up middleware.
"""
import logging
import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .infrastructure.config import settings
from .infrastructure.database import engine, Base
from .domain.services import get_supported_corridors

# Route modules
from .api.routes.auth import router as auth_router
from .api.routes.payments import router as payments_router
from .api.routes.analysis import router as analysis_router
from .api.routes.recommendations import router as recommendations_router
from .api.routes.demo import router as demo_router
from .api.routes.stripe import router as stripe_router

# ─── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO if settings.environment == "production" else logging.DEBUG,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger("xborder")


# ─── Lifespan ────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting XBorder Payment Intelligence [{settings.environment}]")
    logger.info(f"LLM provider: {settings.llm_provider}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created / verified")
    yield
    logger.info("Shutting down")
    await engine.dispose()


# ─── App ─────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="XBorder Payment Intelligence API",
    description="AI-powered cross-border payment analysis -- expose hidden fees, optimize routes",
    version="0.1.0",
    lifespan=lifespan,
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}:\n{traceback.format_exc()}")
    return JSONResponse(status_code=500, content={"detail": str(exc)})


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Include Routers ─────────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(payments_router)
app.include_router(analysis_router)
app.include_router(recommendations_router)
app.include_router(demo_router)
app.include_router(stripe_router)


# ─── Root Endpoints ──────────────────────────────────────────────────────────

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "XBorder Payment Intelligence",
        "version": "0.1.0",
        "environment": settings.environment,
        "llm_provider": settings.llm_provider,
    }


@app.get("/")
async def root():
    return {
        "message": "XBorder Payment Intelligence API",
        "docs": "/docs",
        "health": "/health",
        "corridors": get_supported_corridors(),
    }


# ─── Run ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host=settings.api_host, port=settings.api_port, reload=settings.environment == "development")
