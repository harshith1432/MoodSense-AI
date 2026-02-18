# 🎓 Training Custom Face Emotion Model

## Overview

MoodSense AI works **out of the box** with pretrained DeepFace models. However, you can optionally train a custom model on the DepVidMood facial expression dataset for potentially improved accuracy.

---

## Default vs Custom Model

### ✅ Default (Pretrained DeepFace)
- **Pros**: Works immediately, no training needed, good accuracy
- **Cons**: General-purpose model, may not be optimized for your use case

### 🎯 Custom Trained Model
- **Pros**: Potentially higher accuracy, optimized for specific dataset
- **Cons**: Requires training time (~1-2 hours), needs Kaggle API setup

---

## Prerequisites

### 1. Kaggle API Setup

1. Create a Kaggle account at https://www.kaggle.com
2. Go to Account Settings → API → Create New API Token
3. Download `kaggle.json`
4. Place it in the correct location:
   - **Windows**: `C:\Users\<YourUsername>\.kaggle\kaggle.json`
   - **Linux/Mac**: `~/.kaggle/kaggle.json`

5. Set permissions (Linux/Mac only):
```bash
chmod 600 ~/.kaggle/kaggle.json
```

### 2. Install kagglehub

Already included in requirements.txt:
```bash
pip install kagglehub
```

---

## Training Steps

### Step 1: Run the Training Script

```bash
# Activate your virtual environment first
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Run training
python train_custom_face_model.py
```

### What Happens During Training:

1. **Dataset Download** (~5-10 minutes)
   - Downloads DepVidMood facial expression video dataset from Kaggle
   - Dataset size: ~2-3 GB

2. **Frame Extraction** (~10-20 minutes)
   - Extracts frames from videos
   - Detects faces using OpenCV
   - Preprocesses images (resize, grayscale)

3. **Model Training** (~30-60 minutes)
   - Trains CNN model on extracted frames
   - Uses data augmentation
   - Saves best model based on validation accuracy

4. **Evaluation**
   - Tests on validation set
   - Displays final accuracy

### Step 2: Use the Custom Model

After training completes, you have two options:

#### Option A: Switch Entirely to Custom Model

Edit `api/face_routes.py`:

```python
# Change this:
from modules.face_analyzer import get_face_analyzer

# To this:
from modules.face_analyzer_custom import get_custom_face_analyzer as get_face_analyzer
```

#### Option B: Use Both (Recommended for Testing)

Create a new endpoint in `api/face_routes.py`:

```python
from modules.face_analyzer_custom import get_custom_face_analyzer

@router.post("/analyze/custom")
async def analyze_face_custom(
    image_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Analyze using custom-trained model"""
    # Same logic as analyze_face but uses custom analyzer
    ...
```

---

## Training Configuration

You can customize training in `train_custom_face_model.py`:

```python
# Model save location
MODEL_SAVE_PATH = "model_cache/custom_face_model.h5"

# Image size (48x48 is standard for FER)
IMG_SIZE = 48

# Training parameters
BATCH_SIZE = 32
EPOCHS = 20  # Increase for better accuracy

# Emotion labels
EMOTION_LABELS = ['anger', 'disgust', 'fear', 'joy', 'neutral', 'sadness', 'surprise']
```

---

## Dataset Information

**DepVidMood Facial Expression Video Dataset**
- **Source**: Kaggle (ziya07/depvidmood-facial-expression-video-dataset)
- **Type**: Video dataset with facial expressions
- **Categories**: 7 emotions (anger, disgust, fear, joy, neutral, sadness, surprise)
- **Format**: MP4/AVI videos

---

## Troubleshooting

### Error: "Kaggle credentials not found"
- Make sure `kaggle.json` is in the correct location
- Check file permissions on Linux/Mac

### Error: "Out of memory"
- Reduce `BATCH_SIZE` in the training script
- Reduce number of frames per video
- Close other applications

### Error: "No module named 'kagglehub'"
- Run: `pip install kagglehub`

### Low Accuracy
- Increase `EPOCHS` (try 30-50)
- Use more frames per video (change the limit in code)
- Add data augmentation

---

## Performance Comparison

After training, you can compare:

| Model | Accuracy | Speed | Setup Time |
|-------|----------|-------|------------|
| DeepFace (default) | ~70-75% | Fast | 0 min |
| Custom Trained | ~75-85%* | Fast | 60-120 min |

*Accuracy depends on training time and dataset quality

---

## Advanced: Fine-tuning

For even better results, you can fine-tune the pretrained DeepFace model instead of training from scratch. This typically yields better results with less training time.

Edit `train_custom_face_model.py` and add:

```python
# Load pretrained model as base
from deepface import DeepFace
base_model = DeepFace.build_model("Emotion")

# Freeze early layers
for layer in base_model.layers[:-5]:
    layer.trainable = False

# Continue with training...
```

---

## Questions?

- Check the model training logs in the console
- Verify the saved model exists at `model_cache/custom_face_model.h5`
- Compare results between default and custom model
- Open an issue if you encounter problems

**Remember**: The default DeepFace model works great! Custom training is optional for those who want to experiment or need higher accuracy.
