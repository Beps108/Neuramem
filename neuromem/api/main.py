"""
NeuraMem FastAPI Application
Main API server running on port 8765
"""
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import logging

from neuromem.api.routes import beliefs, rejections, contradictions, traces, audit
from neuromem.core.runtime import get_runtime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    runtime = get_runtime()
    logger.info(f"NeuraMem starting on {runtime.os_type}")
    yield
    # Shutdown
    logger.info("NeuraMem shutting down")


app = FastAPI(
    title="NeuraMem API",
    description="Neural Memory Management System API",
    version="0.1.0",
    lifespan=lifespan
)

# Include routers
app.include_router(beliefs.router, prefix="/api/v1/beliefs", tags=["beliefs"])
app.include_router(rejections.router, prefix="/api/v1/rejections", tags=["rejections"])
app.include_router(contradictions.router, prefix="/api/v1/contradictions", tags=["contradictions"])
app.include_router(traces.router, prefix="/api/v1/traces", tags=["traces"])
app.include_router(audit.router, prefix="/api/v1/audit", tags=["audit"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "NeuraMem API",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8765)
