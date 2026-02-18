"""
MoodSense AI - Simplified FastAPI Application
Version without lifespan for compatibility
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from config import settings

# Create FastAPI app
app = FastAPI(
    title="MoodSense AI",
    description="AI-powered emotional intelligence system for better communication",
    version="1.0.0",
    docs_url="/docs"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
Path(settings.UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)
Path(settings.MODEL_CACHE_DIR).mkdir(parents=True, exist_ok=True)
Path("static/css").mkdir(parents=True, exist_ok=True)
Path("static/js").mkdir(parents=True, exist_ok=True)
Path("templates").mkdir(parents=True, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")


# ============ Routes ============

@app.get("/")
async def home(request: Request):
    """Main application page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "MoodSense AI"
    }


# ============ Import API Routes ============
from api.text_routes import router as text_router
from api.voice_routes import router as voice_router
from api.face_routes import router as face_router
from api.analysis_routes import router as analysis_router

app.include_router(text_router)
app.include_router(voice_router)
app.include_router(face_router)
app.include_router(analysis_router)
