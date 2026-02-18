"""
Combined Analysis API Routes
Multi-modal analysis combining text, voice, and face
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from models.database import get_db, Analysis
from modules.risk_engine import get_risk_engine

router = APIRouter(prefix="/api/analysis", tags=["combined-analysis"])


class CombinedAnalysisRequest(BaseModel):
    text_analysis_id: Optional[int] = None
    voice_analysis_id: Optional[int] = None
    face_analysis_id: Optional[int] = None
    

@router.post("/combined")
async def analyze_combined(
    request: CombinedAnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Perform combined risk analysis from multiple modalities
    """
    try:
        risk_engine = get_risk_engine()
        
        # Fetch analysis results from DB
        text_data = None
        voice_data = None
        face_data = None
        
        if request.text_analysis_id:
            text_analysis = db.query(Analysis).filter(
                Analysis.id == request.text_analysis_id
            ).first()
            if text_analysis:
                text_data = {
                    "emotion": text_analysis.emotion,
                    "risk_level": text_analysis.risk_level,
                    "confidence": text_analysis.confidence
                }
        
        if request.voice_analysis_id:
            voice_analysis = db.query(Analysis).filter(
                Analysis.id == request.voice_analysis_id
            ).first()
            if voice_analysis:
                voice_data = voice_analysis.detailed_results
        
        if request.face_analysis_id:
            face_analysis = db.query(Analysis).filter(
                Analysis.id == request.face_analysis_id
            ).first()
            if face_analysis:
                face_data = {
                    "emotion": face_analysis.emotion,
                    "risk_level": face_analysis.risk_level,
                    "confidence": face_analysis.confidence,
                    "face_detected": True
                }
        
        # Calculate combined risk
        combined_result = risk_engine.calculate_combined_risk(
            text_data=text_data,
            voice_data=voice_data,
            face_data=face_data
        )
        
        # Save combined analysis
        db_analysis = Analysis(
            timestamp=datetime.utcnow(),
            analysis_type="combined",
            emotion=combined_result["dominant_emotion"],
            risk_level=combined_result["risk_level"],
            confidence=combined_result["confidence"],
            detailed_results=combined_result,
            suggestions=combined_result["recommendations"]
        )
        
        db.add(db_analysis)
        db.commit()
        db.refresh(db_analysis)
        
        combined_result["analysis_id"] = db_analysis.id
        
        return combined_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard")
async def get_dashboard_data(
    db: Session = Depends(get_db)
):
    """
    Get dashboard data with recent analyses and statistics
    """
    # Get recent analyses
    recent = db.query(Analysis)\
        .order_by(Analysis.timestamp.desc())\
        .limit(20)\
        .all()
    
    # Calculate statistics
    total_analyses = db.query(Analysis).count()
    
    # Emotion distribution
    emotion_counts = {}
    risk_counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    
    for analysis in recent:
        emotion = analysis.emotion
        emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        risk = analysis.risk_level
        risk_counts[risk] = risk_counts.get(risk, 0) + 1
    
    # Get trend
    risk_engine = get_risk_engine()
    trend = risk_engine.detect_escalation([
        {"risk_level": a.risk_level} for a in recent
    ])
    
    return {
        "total_analyses": total_analyses,
        "recent_count": len(recent),
        "emotion_distribution": emotion_counts,
        "risk_distribution": risk_counts,
        "trend": trend,
        "recent_analyses": [
            {
                "id": a.id,
                "timestamp": a.timestamp.isoformat(),
                "type": a.analysis_type,
                "emotion": a.emotion,
                "risk_level": a.risk_level,
                "confidence": a.confidence
            }
            for a in recent[:10]
        ]
    }


@router.get("/history")
async def get_all_history(
    limit: int = 20,
    analysis_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get analysis history with optional filtering
    """
    query = db.query(Analysis)
    
    if analysis_type:
        query = query.filter(Analysis.analysis_type == analysis_type)
    
    analyses = query.order_by(Analysis.timestamp.desc()).limit(limit).all()
    
    return {
        "count": len(analyses),
        "analyses": [
            {
                "id": a.id,
                "timestamp": a.timestamp.isoformat(),
                "type": a.analysis_type,
                "emotion": a.emotion,
                "risk_level": a.risk_level,
                "confidence": a.confidence,
                "message": a.input_text if a.analysis_type == "text" else None
            }
            for a in analyses
        ]
    }
