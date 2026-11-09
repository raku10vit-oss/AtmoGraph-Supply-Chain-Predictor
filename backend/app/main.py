"""
AtmoGraph – FastAPI Application Entry Point

Run with:
    cd backend
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database.neo4j_connection import neo4j_conn
from app.routes.graph_routes import router

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("atmograph")


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[type-arg]
    logger.info("🚀 AtmoGraph backend starting …")
    try:
        neo4j_conn.connect()
    except Exception as exc:
        logger.warning(
            "⚠️  Neo4j not available at startup (%s). "
            "Graph endpoints will return 500 until Neo4j is reachable.",
            exc,
        )
    yield
    # Shutdown
    neo4j_conn.close()
    logger.info("👋 AtmoGraph backend shut down cleanly.")


# ── App ────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="AtmoGraph API",
    description=(
        "**AtmoGraph – Supply Chain Ripple Effect Predictor** "
        "| Graph analysis backend powered by Neo4j + FastAPI."
    ),
    version="1.0.0",
    contact={"name": "AtmoGraph Team"},
    lifespan=lifespan,
)

# ── CORS ───────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ─────────────────────────────────────────────────────────────────────
app.include_router(router)


@app.get("/", include_in_schema=False)
async def root():
    return {
        "name": "AtmoGraph API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
    }


# ── Dev entrypoint ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )
