"""
FastAPI application entry point.
Career Intelligence API with ML predictions and AI-powered chat advisor.
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import chat

# Path to React build output
STATIC_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

app = FastAPI(
    title="Career Intelligence API",
    description="AI-powered career prediction, skill recommendation, and chat advisor.",
    version="2.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "https://career-intelligence.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(chat.router)


@app.get("/health")
@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {"success": True, "message": "Career Intelligence API is running"}


@app.get("/")
def root():
    """Root endpoint."""
    return {"message": "Career API is running"}


# Serve React static files (production)
if STATIC_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(STATIC_DIR / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_react(full_path: str):
        """Serve the React SPA for all non-API routes."""
        file_path = STATIC_DIR / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(STATIC_DIR / "index.html"))
