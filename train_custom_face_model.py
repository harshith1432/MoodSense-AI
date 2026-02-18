"""
Optional: Train Custom Facial Expression Model
Uses the DepVidMood dataset from Kaggle for enhanced accuracy

NOTE: This is OPTIONAL. The system works with pretrained DeepFace models by default.
Only run this if you want to train a custom model for potentially better accuracy.
"""
import os
import kagglehub
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from pathlib import Path
import cv2
import numpy as np
from sklearn.model_selection import train_test_split

# Configuration
MODEL_SAVE_PATH = "model_cache/custom_face_model.h5"
EMOTION_LABELS = ['anger', 'disgust', 'fear', 'joy', 'neutral', 'sadness', 'surprise']
IMG_SIZE = 48
BATCH_SIZE = 32
EPOCHS = 20


def download_dataset():
    """Download the DepVidMood facial expression dataset from Kaggle"""
    print("📥 Downloading dataset from Kaggle...")
    print("(This may take a while - the dataset is large)")
    
    path = kagglehub.dataset_download("ziya07/depvidmood-facial-expression-video-dataset")
    print(f"✓ Dataset downloaded to: {path}")
    
    return path


def extract_frames_from_videos(dataset_path):
    """Extract frames from videos for training"""
    print("\n🎬 Extracting frames from videos...")
    
    frames = []
    labels = []
    
    dataset_path = Path(dataset_path)
    
    # Process each emotion folder
    for emotion_idx, emotion in enumerate(EMOTION_LABELS):
        emotion_folder = dataset_path / emotion
        
        if not emotion_folder.exists():
            print(f"⚠️  Folder not found: {emotion_folder}")
            continue
        
        video_files = list(emotion_folder.glob("*.mp4")) + list(emotion_folder.glob("*.avi"))
        
        print(f"  Processing {len(video_files)} videos for emotion: {emotion}")
        
        for video_file in video_files[:10]:  # Limit for demo - remove [:10] for full training
            cap = cv2.VideoCapture(str(video_file))
            frame_count = 0
            
            while cap.isOpened() and frame_count < 10:  # Take 10 frames per video
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Convert to grayscale
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Detect face
                face_cascade = cv2.CascadeClassifier(
                    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                )
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                
                if len(faces) > 0:
                    x, y, w, h = faces[0]
                    face_roi = gray[y:y+h, x:x+w]
                    face_resized = cv2.resize(face_roi, (IMG_SIZE, IMG_SIZE))
                    
                    frames.append(face_resized)
                    labels.append(emotion_idx)
                    frame_count += 1
            
            cap.release()
        
        print(f"  ✓ Extracted {len([l for l in labels if l == emotion_idx])} frames for {emotion}")
    
    return np.array(frames), np.array(labels)


def create_model():
    """Create CNN model for facial expression recognition"""
    print("\n🏗️  Building model architecture...")
    
    model = keras.Sequential([
        # Input layer
        layers.Input(shape=(IMG_SIZE, IMG_SIZE, 1)),
        
        # Convolutional blocks
        layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D(2, 2),
        layers.Dropout(0.25),
        
        layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D(2, 2),
        layers.Dropout(0.25),
        
        layers.Conv2D(256, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D(2, 2),
        layers.Dropout(0.25),
        
        # Dense layers
        layers.Flatten(),
        layers.Dense(256, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        
        layers.Dense(128, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        
        # Output layer
        layers.Dense(len(EMOTION_LABELS), activation='softmax')
    ])
    
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    print("✓ Model created")
    model.summary()
    
    return model


def train_model(X_train, y_train, X_val, y_val):
    """Train the model"""
    print("\n🎯 Training model...")
    print(f"Training samples: {len(X_train)}")
    print(f"Validation samples: {len(X_val)}")
    
    model = create_model()
    
    # Callbacks
    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=5,
            restore_best_weights=True
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=3
        ),
        keras.callbacks.ModelCheckpoint(
            MODEL_SAVE_PATH,
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1
        )
    ]
    
    # Normalize data
    X_train = X_train.astype('float32') / 255.0
    X_val = X_val.astype('float32') / 255.0
    
    # Add channel dimension
    X_train = np.expand_dims(X_train, -1)
    X_val = np.expand_dims(X_val, -1)
    
    # Train
    history = model.fit(
        X_train, y_train,
        batch_size=BATCH_SIZE,
        epochs=EPOCHS,
        validation_data=(X_val, y_val),
        callbacks=callbacks,
        verbose=1
    )
    
    return model, history


def main():
    """Main training pipeline"""
    print("="*60)
    print("  Custom Face Emotion Model Training")
    print("="*60)
    
    # Create model cache directory
    Path("model_cache").mkdir(exist_ok=True)
    
    # Step 1: Download dataset
    dataset_path = download_dataset()
    
    # Step 2: Extract and preprocess frames
    X, y = extract_frames_from_videos(dataset_path)
    
    print(f"\n📊 Total samples: {len(X)}")
    print(f"Samples per class: {[len(y[y==i]) for i in range(len(EMOTION_LABELS))]}")
    
    # Step 3: Split data
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Step 4: Train model
    model, history = train_model(X_train, y_train, X_val, y_val)
    
    # Step 5: Evaluate
    print("\n📈 Final Results:")
    val_loss, val_acc = model.evaluate(X_val, y_val, verbose=0)
    print(f"Validation Loss: {val_loss:.4f}")
    print(f"Validation Accuracy: {val_acc:.4f}")
    
    print("\n✅ Training complete!")
    print(f"Model saved to: {MODEL_SAVE_PATH}")
    print("\nTo use this custom model, update face_analyzer.py to load this model instead of DeepFace.")


if __name__ == "__main__":
    # Check if Kaggle credentials are configured
    if not os.path.exists(os.path.expanduser("~/.kaggle/kaggle.json")):
        print("⚠️  Kaggle credentials not found!")
        print("Please set up Kaggle API credentials first:")
        print("1. Go to https://www.kaggle.com/settings")
        print("2. Create a new API token")
        print("3. Place kaggle.json in ~/.kaggle/")
        exit(1)
    
    main()
