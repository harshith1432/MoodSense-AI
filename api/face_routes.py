"""
Face Analysis API Routes - TEMPORARILY DISABLED
Requires Python 3.11 for TensorFlow compatibility
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import cv2
import numpy as np
import logging
from datetime import datetime

from models.database import get_db, Analysis
from modules.face_analyzer import get_face_analyzer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/face", tags=["face-analysis"])


@router.post("/analyze")
async def analyze_face(
    image_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Analyze facial expression
    """
    try:
        # Validate file
        contents = await image_file.read()
        nparr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image file")

        # Analyze face
        face_analyzer = get_face_analyzer()
        analysis_result = face_analyzer.analyze_face(frame)
        
        # Save to database
        db_analysis = Analysis(
            timestamp=datetime.utcnow(),
            analysis_type="face",
            audio_path=None, # Reusing column or adding new one? Database has audio_path. 
            # We don't have image_path column in Analysis model shown in database.py view earlier (line 32 audio_path). 
            # It has detailed_results.
            emotion=analysis_result["emotion"],
            risk_level=analysis_result.get("risk_level", "LOW"),
            confidence=analysis_result["confidence"],
            detailed_results=analysis_result,
            suggestions=analysis_result.get("suggested_replies"),
            warnings=analysis_result.get("advice", {}).get("things_to_avoid")
        )
        
        db.add(db_analysis)
        db.commit()
        db.refresh(db_analysis)
        
        return {
            **analysis_result,
            "analysis_id": db_analysis.id
        }
        
    except Exception as e:
        logger.error(f"Face analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_face_history(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get recent face analyses"""
    
    return {
        "count": 0,
        "analyses": [],
        "message": "Face analysis temporarily disabled"
    }
