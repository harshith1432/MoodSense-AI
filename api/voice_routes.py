"""
Voice Analysis API Routes
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import os
from pathlib import Path

from models.database import get_db, Analysis
from modules.voice_analyzer import get_voice_analyzer
from config import settings

router = APIRouter(prefix="/api/voice", tags=["voice-analysis"])

# Ensure upload directory exists
Path(settings.UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)


@router.post("/analyze")
async def analyze_voice(
    audio_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Analyze voice tone from uploaded audio file
    """
    try:
        # Validate file extension
        file_ext = Path(audio_file.filename).suffix.lower()
        if file_ext not in settings.ALLOWED_AUDIO_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {settings.ALLOWED_AUDIO_EXTENSIONS}"
            )
        
        # Validate file size
        contents = await audio_file.read()
        file_size_mb = len(contents) / (1024 * 1024)
        if file_size_mb > settings.MAX_AUDIO_SIZE_MB:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {settings.MAX_AUDIO_SIZE_MB}MB"
            )
        
        # Save file temporarily
        file_path = Path(settings.UPLOAD_FOLDER) / f"voice_{datetime.now().timestamp()}{file_ext}"
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Analyze voice
        voice_analyzer = get_voice_analyzer()
        analysis_result = voice_analyzer.analyze_voice(str(file_path))
        
        # Save to database
        db_analysis = Analysis(
            timestamp=datetime.utcnow(),
            analysis_type="voice",
            audio_path=str(file_path),
            emotion=analysis_result["emotion"],
            risk_level=analysis_result["risk_level"],
            confidence=analysis_result["stress_level"],  # Using stress as confidence proxy
            detailed_results=analysis_result,
            suggestions=analysis_result.get("suggested_replies"),
            warnings=analysis_result.get("advice", {}).get("things_to_avoid")
        )
        
        db.add(db_analysis)
        db.commit()
        db.refresh(db_analysis)
        
        # Clean up file (optionally keep based on settings)
        if not settings.ALLOW_IMAGE_STORAGE:
            os.remove(file_path)
            analysis_result["file_removed"] = True
        
        return {
            **analysis_result,
            "analysis_id": db_analysis.id
        }
        
    except Exception as e:
        # Clean up file on error
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_voice_history(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get recent voice analyses
    """
    analyses = db.query(Analysis)\
        .filter(Analysis.analysis_type == "voice")\
        .order_by(Analysis.timestamp.desc())\
        .limit(limit)\
        .all()
    
    return {
        "count": len(analyses),
        "analyses": [
            {
                "id": a.id,
                "timestamp": a.timestamp.isoformat(),
                "emotion": a.emotion,
                "risk_level": a.risk_level,
                "tone": a.detailed_results.get("tone") if a.detailed_results else None
            }
            for a in analyses
        ]
    }
