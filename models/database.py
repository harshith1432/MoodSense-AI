"""
Database models and session management for MoodSense AI
Using PostgreSQL (Neon) as the database
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import settings

# Database connection
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Analysis(Base):
    """Store individual mood analyses"""
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    analysis_type = Column(String(20))  # 'text', 'voice', 'face', 'combined'
    
    # Input data
    input_text = Column(Text, nullable=True)
    audio_path = Column(String(255), nullable=True)
    
    # Results
    emotion = Column(String(50))
    risk_level = Column(String(20))  # LOW, MEDIUM, HIGH, CRITICAL
    confidence = Column(Float)
    
    # Detailed results (JSON)
    detailed_results = Column(JSON)  # stores all analysis data
    suggestions = Column(JSON)  # array of suggestions
    warnings = Column(JSON)  # things to avoid
    
    # Conversation tracking
    conversation_id = Column(Integer, nullable=True)


class Conversation(Base):
    """Track conversation history and trends"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Conversation data
    messages = Column(JSON)  # array of {timestamp, text, emotion, risk_level}
    risk_trend = Column(String(20))  # 'escalating', 'stable', 'improving'
    
    # Summary stats
    total_messages = Column(Integer, default=0)
    avg_risk_score = Column(Float, default=0.0)
    dominant_emotion = Column(String(50))


class UserSettings(Base):
    """User preferences and consent"""
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Privacy & Consent
    webcam_consent = Column(Boolean, default=False)
    microphone_consent = Column(Boolean, default=False)
    data_storage_consent = Column(Boolean, default=False)
    
    # Preferences
    theme = Column(String(20), default="dark")
    notification_preferences = Column(JSON)


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session (for FastAPI dependency injection)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
