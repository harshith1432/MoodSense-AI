"""
MoodSense AI - Minimal Working Server
Loads models on-demand to avoid startup issues
"""
import uvicorn

if __name__ == "__main__":
    # Initialize database before starting server
    print("📊 Initializing database...")
    from models.database import init_db
    init_db()
    print("✓ Database ready")
    
    print("🚀 Starting MoodSense AI server...")
    print("📝 Models will load on first API request")
    print("🌐 Open http://localhost:8000 in your browser")
    
    uvicorn.run(
        "app_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
