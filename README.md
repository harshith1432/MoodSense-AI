# 🧠 MoodSense AI

> **AI-Powered Emotional Intelligence System for Better Communication**

MoodSense AI analyzes emotional signals from text, voice, and facial expressions to detect mood and provide communication guidance - helping you prevent misunderstandings and improve emotional understanding.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)
![HuggingFace](https://img.shields.io/badge/HuggingFace-Transformers-yellow.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue.svg)

---

## 🌟 Features

### 📝 Phase 1: Text Mood Analyzer
- **Emotion Detection**: Detects 7+ emotions including anger, sadness, joy, sarcasm, and passive-aggression
- **Risk Assessment**: Categorizes conversations as LOW, MEDIUM, HIGH, or CRITICAL risk
- **Communication Guidance**: Provides suggested responses and warnings on what to avoid
- **Smart Suggestions**: AI-powered advice tailored to each emotional state

### 💬 Phase 2: Smart Reply Generator
- **Emotionally Intelligent Replies**: Generate 3-5 safe, empathetic response suggestions
- **Context-Aware**: Responses adapt based on detected emotion and risk level
- **Toxic Content Filtering**: Automatically filters out potentially harmful replies
- **Ranked Responses**: Prioritizes empathy-first communication

### 🎤 Phase 3: Voice Tone Analyzer
- **Audio Feature Extraction**: Analyzes pitch, volume, speech rate, and energy
- **Tone Classification**: Detects tones like Angry, Anxious, Calm, or Excited
- **Stress Level Detection**: Calculates vocal stress from 0-100%
- **Multi-Format Support**: Accepts WAV, MP3, M4A, OGG files

### 😊 Phase 4: Facial Emotion Detection
- **Real-Time Expression Analysis**: Detects emotions from uploaded photos
- **7 Emotion Categories**: Happy, Sad, Angry, Surprised, Fear, Disgust, Neutral
- **Confidence Scoring**: Provides reliability metrics for each detection
- **Privacy-First Design**: No image storage without explicit consent

### 🚨 Final System: Relationship Risk Engine
- **Multi-Modal Fusion**: Combines text, voice, and facial signals
- **Weighted Risk Calculation**: Intelligent fusion of all emotional signals
- **Trend Analysis**: Detects if situations are escalating or improving
- **Actionable Recommendations**: Specific guidance based on combined assessment

---

## 🛠 Tech Stack

### Backend
- **Framework**: FastAPI (async Python web framework)
- **Database**: PostgreSQL (via Neon)
- **ORM**: SQLAlchemy

### AI/ML
- **NLP**: HuggingFace Transformers
  - Emotion: `j-hartmann/emotion-english-distilroberta-base`
  - Sarcasm: `helinivan/english-sarcasm-detector`
  - Sentiment: `cardiffnlp/twitter-roberta-base-sentiment-latest`
- **Audio Processing**: Librosa, NumPy
- **Computer Vision**: DeepFace, OpenCV, TensorFlow

### Frontend
- **HTML5/CSS3/JavaScript** (Vanilla)
- **Modern Glassmorphism Design**
- **Responsive Layout**
- **Google Fonts**: Inter + Outfit

---

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- PostgreSQL database (or use Neon free tier)

### Steps

1. **Clone the repository**
```bash
git clone <repository-url>
cd "MoodSense AI"
```

2. **Create virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
# Copy the example file
copy .env.example .env

# Edit .env and add your PostgreSQL connection string
# DATABASE_URL=postgresql://user:pass@host/dbname
```

5. **Initialize database**
```bash
python -c "from models.database import init_db; init_db()"
```

6. **Run the application**
```bash
python app.py
```

7. **Open your browser**
```
http://localhost:8000
```

---

## 🚀 Usage

### Text Analysis
1. Navigate to the **Text Analyzer** tab
2. Enter a message (e.g., "Fine. Do whatever you want.")
3. Click **Analyze Message**
4. View detected emotion, risk level, and communication guidance
5. Copy suggested replies with one click

### Voice Analysis
1. Navigate to the **Voice Analyzer** tab
2. Upload an audio file (WAV, MP3, M4A, or OGG)
3. Click **Analyze Voice**
4. View tone classification, stress level, and audio features

### Face Analysis
1. Navigate to the **Face Analyzer** tab
2. Read and acknowledge the privacy notice
3. Upload a clear photo showing your face
4. Click **Analyze Expression**
5. View detected emotion and confidence breakdown

### Dashboard
1. Navigate to the **Dashboard** tab
2. View total analyses, risk/emotion distributions
3. See recent analysis history
4. Track trends (escalating, stable, improving)

---

## 📊 API Documentation

Once the server is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Key Endpoints

#### Text Analysis
```http
POST /api/text/analyze
Content-Type: application/json

{
  "message": "Your message here",
  "conversation_id": 1  // optional
}
```

#### Voice Analysis
```http
POST /api/voice/analyze
Content-Type: multipart/form-data

audio_file: <file>
```

#### Face Analysis
```http
POST /api/face/analyze
Content-Type: multipart/form-data

image_file: <image>
```

#### Dashboard Data
```http
GET /api/analysis/dashboard
```

---

## 🗂 Project Structure

```
moodsense-ai/
├── app.py                      # FastAPI main application
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
│
├── modules/                    # Core AI modules
│   ├── text_analyzer.py       # Text mood detection
│   ├── advice_engine.py       # Guidance generation
│   ├── reply_generator.py     # Smart reply system
│   ├── voice_analyzer.py      # Voice tone analysis
│   ├── face_analyzer.py       # Facial emotion detection
│   └── risk_engine.py         # Multi-modal risk assessment
│
├── models/                     # Database models
│   └── database.py            # SQLAlchemy models
│
├── api/                       # API routes
│   ├── text_routes.py
│   ├── voice_routes.py
│   ├── face_routes.py
│   └── analysis_routes.py
│
├── static/                    # Frontend assets
│   ├── css/style.css
│   ├── js/main.js
│   └── uploads/               # Temporary file storage
│
├── templates/
│   └── index.html             # Main web interface
│
├── model_cache/               # HuggingFace model cache
├── ETHICS.md                  # Ethical guidelines
└── README.md                  # This file
```

---

## ⚖️ Ethical Considerations

MoodSense AI is designed with privacy and ethics in mind:

- ✅ **Consent Required**: Explicit permission before webcam/microphone access
- ✅ **No Data Storage**: Images/audio not stored by default
- ✅ **Transparency**: Clear indication of what's being analyzed
- ✅ **Privacy-First**: All processing happens locally or securely
- ✅ **Not a Replacement**: Does not replace professional mental health support

See [ETHICS.md](ETHICS.md) for full ethical statement.

---

## 🎯 Use Cases

- **Relationship Communication**: Avoid miscommunication with your partner
- **Customer Support**: Detect customer frustration early
- **Team Management**: Understand team morale and stress levels
- **Mental Health Awareness**: Track your own emotional patterns
- **Conflict Resolution**: De-escalate tense conversations

---

## 🎓 Custom Model Training (Optional)

The system uses **pretrained DeepFace models** by default and works immediately. However, you can optionally train a custom facial expression model on the **DepVidMood dataset** for enhanced accuracy.

### Quick Start:

```bash
# 1. Set up Kaggle API credentials (see TRAINING.md)
# 2. Run training script
python train_custom_face_model.py

# 3. Model will be saved to model_cache/custom_face_model.h5
```

**See [TRAINING.md](TRAINING.md) for detailed instructions.**

### Benefits:
- ✅ Potentially higher accuracy (~5-10% improvement)
- ✅ Optimized for specific use cases
- ✅ Uses video-based DepVidMood dataset from Kaggle

**Note**: Training takes ~1-2 hours. The default model works great if you don't need this!

---

## 🚧 Roadmap

- [ ] Real-time webcam support (WebSocket streaming)
- [x] Custom face model training option
- [ ] Multi-language support
- [ ] Browser extension for email/chat analysis
- [ ] Mobile app (React Native)
- [ ] Conversation memory and trend analysis
- [ ] Integration with Slack/Discord
- [ ] Voice response (TTS) for guidance

---

## 🤝 Contributing

Contributions welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **HuggingFace** for transformer models
- **DeepFace** for facial emotion recognition
- **Librosa** for audio analysis
- **FastAPI** for the amazing web framework
- **Neon** for PostgreSQL hosting

---

## 📧 Contact

For questions, suggestions, or support, please open an issue on GitHub.

---

**Made with ❤️ and 🧠 by MoodSense AI Team**

*Improving emotional intelligence, one conversation at a time.*

# MoodSense-AI
