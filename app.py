"""
MoodSense AI - Main FastAPI Application
Emotionally intelligent communication assistant
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import logging
from contextlib import asynccontextmanager

from config import settings
from models.database import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============ Lifespan Event ============
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and load models on startup"""
    logger.info("🚀 Starting MoodSense AI...")
    
    # Initialize database
    logger.info("📊 Initializing database...")
    init_db()
    logger.info("✓ Database ready")
    
    # Pre-load AI models
    logger.info("🤖 Loading AI models...")
    try:
        from modules.text_analyzer import get_text_analyzer
        get_text_analyzer()
        logger.info("✓ Text analyzer loaded")
    except Exception as e:
        logger.error(f"⚠️ Error loading text analyzer: {e}")
    
    logger.info("✅ MoodSense AI is ready!")
    
    yield  # Application runs
    
    # Cleanup (if needed)
    logger.info("Shutting down...")

# Create FastAPI app with lifespan
app = FastAPI(
    title="MoodSense AI",
    description="AI-powered emotional intelligence system for better communication",
    version="1.0.0",
    docs_url="/docs",
    lifespan=lifespan
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


# ============ Run Application ============
if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server on {settings.APP_HOST}:{settings.APP_PORT}")
    
    uvicorn.run(
        "app:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning"
    )
