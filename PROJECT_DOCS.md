# MoodSense AI - Project Documentation 📚

## 1. 🏗️ Architecture Overview

MoodSense AI follows a modern client-server architecture:

- **Frontend**: A responsive web interface built with standard HTML, CSS, and JavaScript. It handles media capture (audio/video), user input, and result visualization.
- **Backend API**: A high-performance Python application using **FastAPI**. It routes requests to specific analysis modules.
- **Analysis Modules**: Specialized Python classes for processing different data types.
    - `TextAnalyzer`: NLP processing.
    - `VoiceAnalyzer`: Audio feature extraction.
    - `FaceAnalyzer`: Computer vision and deep learning.
- **Database**: An SQL-based storage layer (managed via SQLAlchemy) for persisting analysis results and conversation history.

## 2. 🔌 API Endpoints

### Text Analysis
- **POST** `/api/text/analyze`
    - **Input**: JSON `{"text": "I am feeling great!"}`
    - **Output**: Emotion, Risk Level, Suggestions, Advice.

### Voice Analysis
- **POST** `/api/voice/analyze`
    - **Input**: `multipart/form-data` (Audio File)
    - **Output**: Tone, Emotion, Pitch/Volume Metrics, Suggestions.
    - **Logic**: Extracts audio features using `librosa` and maps them to emotional states.

### Face Analysis
- **POST** `/api/face/analyze`
    - **Input**: `multipart/form-data` (Image File)
    - **Output**: Facial Emotion (e.g., "Happy", "Surprise"), Confidence Score.
    - **Logic**: 
        1. Tries `DeepFace` for advanced emotion recognition.
        2. Falls back to `OpenCV` Haar Cascades for basic face detection if DeepFace fails.

## 3. 🗄️ Database Schema

The application uses SQLAlchemy ORM. Key models include:

### `Analysis` Table
Stores individual analysis records.
- `id`: Primary Key
- `timestamp`: Time of analysis
- `analysis_type`: 'text', 'voice', or 'face'
- `emotion`: Detected primary emotion
- `risk_level`: Assessed risk (LOW, MEDIUM, HIGH)
- `confidence`: Confidence score of the model
- `detailed_results`: JSON blob with granular data (e.g., feature vectors)
- `suggestions`: JSON list of suggested replies
- `warnings`: JSON list of advice/warnings

## 4. 🧠 AI & Logic Details

### Advice Engine
The system doesn't just label emotions; it provides guidance.
- **Input**: Emotion + Risk Level.
- **Output**: "Things to Avoid" (e.g., "Don't be defensive") and generic advice.

### Reply Generator
Generates context-aware responses.
- **Input**: Detected Mood.
- **Output**: A list of 3-5 potential replies the user can use.

## 5. 🛡️ Error Handling & Safety

- **Graceful Degradation**: The Face Analysis module is designed to work even if heavy deep-learning libraries fail to load.
- **Input Validation**: Configurable limits on file size and types for uploads.
- **Privacy**: No external cloud APIs are used for analysis; everything runs on the host server.
