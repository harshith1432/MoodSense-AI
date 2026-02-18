# MoodSense AI 🧠✨

**MoodSense AI** is an advanced emotional intelligence platform that analyzes user sentiment through multiple modalities: **Text**, **Voice**, and **Facial Expressions**. It provides real-time feedback, actionable advice, and suggested responses to help users navigate social interactions and manage their emotional well-being.

## 🚀 Features

### 1. 📝 Text Analysis
- **Emotion Detection**: Identifies emotions (Joy, Sadness, Anger, Fear, etc.) from text input.
- **Risk Assessment**: Flags potentially harmful or high-stress content.
- **Smart Suggestions**: Generating context-aware reply suggestions.
- **Advice Engine**: Offers "Things to Avoid" based on the detected tone.

### 2. 🎤 Voice Analysis
- **Tone & Stress Detection**: Analyzes audio recordings for pitch, volume, speech rate, and energy.
- **Detailed Metrics**: Visualizes voice features like "High Pitch" or "Fast Speech Rate".
- **Actionable Feedback**: Provides specific advice and suggested replies based on vocal tone.
- **Support**: Upload audio files or record directly in the browser.

### 3. 😊 Face Analysis
- **Expression Recognition**: Detects facial emotions using computer vision.
- **Live Camera Support**: Capture photos directly from your webcam.
- **Robust Fallback**: Uses advanced AI (`DeepFace`) for precision, with a smart fallback to **OpenCV** for basic detection if deep learning libraries are unavailable.

### 4. � History & Tracking
- **Interaction Log**: Saves analysis history to track emotional trends over time.
- **Privacy First**: Analysis data is processed locally where possible and stored securely.

## 🛠️ Tech Stack

- **Backend**: Python (FastAPI)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Database**: SQLAlchemy (SQLite/PostgreSQL)
- **AI/ML Libraries**:
    - **Text**: HuggingFace Transformers
    - **Voice**: Librosa, NumPy
    - **Face**: DeepFace, OpenCV (cv2)

## 📦 Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/harshith1432/MoodSense-AI.git
    cd "MoodSense AI"
    ```

2.  **Create a Virtual Environment** (Recommended)
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```
    *Note: For full face analysis capabilities, ensure you have the necessary system libraries for OpenCV and TensorFlow.*

## 🚀 Usage

1.  **Start the Server**
    Run the application using `uvicorn`:
    ```bash
    python -m uvicorn app_simple:app --host 0.0.0.0 --port 8001
    ```

2.  **Access the App**
    Open your browser and navigate to:
    **[http://localhost:8001](http://localhost:8001)**

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any enhancements.

## 📄 License

This project is licensed under the MIT License.
