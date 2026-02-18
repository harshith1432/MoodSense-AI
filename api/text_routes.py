"""
Text Analysis API Routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from models.database import get_db, Analysis
from modules.text_analyzer import get_text_analyzer
from modules.advice_engine import get_advice_engine
from modules.reply_generator import get_reply_generator

router = APIRouter(prefix="/api/text", tags=["text-analysis"])


class TextAnalysisRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None


class TextAnalysisResponse(BaseModel):
    emotion: str
    risk_level: str
    confidence: float
    detailed_results: dict
    advice: dict
    suggested_replies: list
    analysis_id: int


@router.post("/analyze", response_model=TextAnalysisResponse)
async def analyze_text(
    request: TextAnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze text message for emotion and provide guidance
    """
    try:
        # Get analyzer instances
        text_analyzer = get_text_analyzer()
        advice_engine = get_advice_engine()
        reply_gen = get_reply_generator()
        
        # Analyze text
        analysis_result = text_analyzer.analyze_text(request.message)
        
        # Generate advice
        advice = advice_engine.generate_advice(
            emotion=analysis_result["emotion"],
            risk_level=analysis_result["risk_level"]
        )
        
        # Generate reply suggestions
        replies = reply_gen.generate_replies(
            mood=analysis_result["emotion"],
            message=request.message
        )
        
        # Save to database
        db_analysis = Analysis(
            timestamp=datetime.utcnow(),
            analysis_type="text",
            input_text=request.message,
            emotion=analysis_result["emotion"],
            risk_level=analysis_result["risk_level"],
            confidence=analysis_result["confidence"],
            detailed_results=analysis_result["detailed_results"],
            suggestions=replies,
            warnings=advice["things_to_avoid"],
            conversation_id=request.conversation_id
        )
        
        db.add(db_analysis)
        db.commit()
        db.refresh(db_analysis)
        
        return {
            "emotion": analysis_result["emotion"],
            "risk_level": analysis_result["risk_level"],
            "confidence": analysis_result["confidence"],
            "detailed_results": analysis_result["detailed_results"],
            "advice": advice,
            "suggested_replies": replies,
            "analysis_id": db_analysis.id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_analysis_history(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get recent text analyses
    """
    analyses = db.query(Analysis)\
        .filter(Analysis.analysis_type == "text")\
        .order_by(Analysis.timestamp.desc())\
        .limit(limit)\
        .all()
    
    return {
        "count": len(analyses),
        "analyses": [
            {
                "id": a.id,
                "timestamp": a.timestamp.isoformat(),
                "message": a.input_text,
                "emotion": a.emotion,
                "risk_level": a.risk_level,
                "confidence": a.confidence
            }
            for a in analyses
        ]
    }
