"""
Quick Test Script for MoodSense AI
Tests basic functionality of all modules
"""
import sys
sys.path.append('.')

def test_text_analyzer():
    """Test text analysis"""
    print("\n🧪 Testing Text Analyzer...")
    
    from modules.text_analyzer import get_text_analyzer
    from modules.advice_engine import get_advice_engine
    from modules.reply_generator import get_reply_generator
    
    analyzer = get_text_analyzer()
    advice_engine = get_advice_engine()
    reply_gen = get_reply_generator()
    
    test_message = "Fine. Do whatever you want."
    
    print(f"  Input: '{test_message}'")
    
    result = analyzer.analyze_text(test_message)
    print(f"  ✓ Emotion: {result['emotion']}")
    print(f"  ✓ Risk Level: {result['risk_level']}")
    print(f"  ✓ Confidence: {result['confidence']}")
    
    advice = advice_engine.generate_advice(result['emotion'], result['risk_level'])
    print(f"  ✓ Generated advice")
    
    replies = reply_gen.generate_replies(result['emotion'], test_message)
    print(f"  ✓ Generated {len(replies)} reply suggestions")
    
    return True

def test_database():
    """Test database connection"""
    print("\n🧪 Testing Database...")
    
    from models.database import init_db, SessionLocal, Analysis
    from datetime import datetime
    
    # Initialize database
    init_db()
    print("  ✓ Database initialized")
    
    # Test insertion
    db = SessionLocal()
    test_analysis = Analysis(
        timestamp=datetime.utcnow(),
        analysis_type="test",
        emotion="neutral",
        risk_level="LOW",
        confidence=0.9,
        detailed_results={"test": True}
    )
    
    db.add(test_analysis)
    db.commit()
    print("  ✓ Test record inserted")
    
    # Test query
    count = db.query(Analysis).count()
    print(f"  ✓ Total analyses: {count}")
    
    # Cleanup
    db.delete(test_analysis)
    db.commit()
    db.close()
    print("  ✓ Test record cleaned up")
    
    return True

def main():
    """Run all tests"""
    print("="*50)
    print("  MoodSense AI - Quick Test Suite")
    print("="*50)
    
    tests = [
        ("Database Connection", test_database),
        ("Text Analyzer", test_text_analyzer),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, "✅ PASS"))
        except Exception as e:
            results.append((test_name, f"❌ FAIL: {str(e)}"))
            print(f"  ❌ Error: {e}")
    
    print("\n" + "="*50)
    print("  Test Results")
    print("="*50)
    
    for test_name, result in results:
        print(f"  {test_name}: {result}")
    
    print("\n✨ Testing complete!")

if __name__ == "__main__":
    main()
