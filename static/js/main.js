// ==================== MAIN APPLICATION LOGIC ====================

// Tab Navigation
const tabButtons = document.querySelectorAll('.tab-btn');
const tabPanes = document.querySelectorAll('.tab-pane');

tabButtons.forEach(button => {
    button.addEventListener('click', () => {
        const tabName = button.dataset.tab;

        // Update active states
        tabButtons.forEach(btn => btn.classList.remove('active'));
        tabPanes.forEach(pane => pane.classList.remove('active'));

        button.classList.add('active');
        document.getElementById(`${tabName}-tab`).classList.add('active');

        // Load dashboard data when switching to dashboard
        if (tabName === 'dashboard') {
            loadDashboard();
        }
    });
});

// Loading Overlay
function showLoading() {
    document.getElementById('loading').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
}

// ==================== TEXT ANALYZER ====================

const textInput = document.getElementById('text-input');
const analyzeTextBtn = document.getElementById('analyze-text-btn');
const textResults = document.getElementById('text-results');

analyzeTextBtn.addEventListener('click', async () => {
    const message = textInput.value.trim();

    if (!message) {
        alert('Please enter a message to analyze');
        return;
    }

    showLoading();

    try {
        const response = await fetch('/api/text/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });

        const data = await response.json();

        if (response.ok) {
            displayTextResults(data);
        } else {
            alert('Error: ' + (data.detail || 'Analysis failed'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to analyze text. Please try again.');
    } finally {
        hideLoading();
    }
});

function displayTextResults(data) {
    // Show results section
    textResults.classList.remove('hidden');

    // Display emotion
    document.getElementById('text-emotion').textContent = data.emotion;

    // Display risk level with color
    const riskElement = document.getElementById('text-risk');
    riskElement.textContent = data.risk_level;
    riskElement.className = `result-value risk-badge risk-${data.risk_level}`;

    // Display confidence
    document.getElementById('text-confidence').textContent =
        `${(data.confidence * 100).toFixed(1)}%`;

    // Display suggested response
    document.getElementById('text-suggestion').textContent =
        data.advice.suggested_response;

    // Display things to avoid
    const avoidList = document.getElementById('text-avoid');
    avoidList.innerHTML = '';
    data.advice.things_to_avoid.forEach(item => {
        const li = document.createElement('li');
        li.textContent = item;
        avoidList.appendChild(li);
    });

    // Display suggested replies
    const repliesGrid = document.getElementById('text-replies');
    repliesGrid.innerHTML = '';
    data.suggested_replies.forEach(reply => {
        const replyDiv = document.createElement('div');
        replyDiv.className = 'reply-option';
        replyDiv.textContent = reply;
        replyDiv.addEventListener('click', () => {
            navigator.clipboard.writeText(reply);
            alert('Reply copied to clipboard!');
        });
        repliesGrid.appendChild(replyDiv);
    });

    // Scroll to results
    textResults.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// ==================== VOICE ANALYZER ====================

const voiceUpload = document.getElementById('voice-upload');
const voiceUploadBtn = document.getElementById('voice-upload-btn');
const analyzeVoiceBtn = document.getElementById('analyze-voice-btn');
const voiceFileName = document.getElementById('voice-file-name');
const voiceResults = document.getElementById('voice-results');

// New Voice Recording Elements
const recordVoiceBtn = document.getElementById('record-voice-btn');
const recordingControls = document.getElementById('recording-controls');
const stopRecordingBtn = document.getElementById('stop-recording-btn');
const recordingTime = document.getElementById('recording-time');

let selectedVoiceFile = null;
let mediaRecorder = null;
let audioChunks = [];
let recordingTimer = null;
let scriptProcessor = null; // For visualization if needed implemented later

voiceUploadBtn.addEventListener('click', () => {
    voiceUpload.click();
});

voiceUpload.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        selectedVoiceFile = file;
        voiceFileName.textContent = `Selected: ${file.name}`;
        voiceFileName.classList.remove('hidden');
        analyzeVoiceBtn.classList.remove('hidden');
    }
});

analyzeVoiceBtn.addEventListener('click', async () => {
    if (!selectedVoiceFile) {
        alert('Please select an audio file first');
        return;
    }

    showLoading();

    const formData = new FormData();
    formData.append('audio_file', selectedVoiceFile);

    try {
        const response = await fetch('/api/voice/analyze', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            displayVoiceResults(data);
        } else {
            alert('Error: ' + (data.detail || 'Analysis failed'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to analyze voice. Please try again.');
    } finally {
        hideLoading();
    }
});

// --- Voice Recording Logic ---

if (recordVoiceBtn) {
    recordVoiceBtn.addEventListener('click', async () => {
        console.log("Voice Record button clicked");

        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            alert("Your browser does not support audio recording. Please use a modern browser (Chrome/Edge/Firefox) and ensure you are on HTTPS or localhost.");
            return;
        }

        try {
            console.log("Requesting microphone access...");
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            console.log("Microphone access granted");
            startRecording(stream);
        } catch (err) {
            console.error('Error accessing microphone:', err);
            alert('Could not access microphone: ' + err.message + '. Please ensure you have granted permission.');
        }
    });
} else {
    console.error("Record Voice button not found in DOM");
}

stopRecordingBtn.addEventListener('click', () => {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
        stopTimer();

        // UI Updates
        recordingControls.classList.add('hidden');
        recordVoiceBtn.classList.remove('hidden');
        voiceUploadBtn.parentElement.classList.remove('hidden'); // Show upload section again
    }
});

function startRecording(stream) {
    audioChunks = [];
    mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
    };

    mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });

        // Stop all tracks to release microphone
        stream.getTracks().forEach(track => track.stop());

        // Analyze the recorded blob
        await analyzeVoiceBlob(audioBlob);
    };

    mediaRecorder.start();
    startTimer();

    // UI Updates
    recordVoiceBtn.classList.add('hidden');
    voiceUploadBtn.parentElement.classList.add('hidden'); // Hide upload section
    recordingControls.classList.remove('hidden');
    voiceResults.classList.add('hidden');
    selectedVoiceFile = null;
    voiceFileName.classList.add('hidden');
    analyzeVoiceBtn.classList.add('hidden');
}

function startTimer() {
    let seconds = 0;
    recordingTime.textContent = '00:00';

    clearInterval(recordingTimer);
    recordingTimer = setInterval(() => {
        seconds++;
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        recordingTime.textContent =
            `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }, 1000);
}

function stopTimer() {
    clearInterval(recordingTimer);
}

async function analyzeVoiceBlob(blob) {
    showLoading();

    const formData = new FormData();
    // Create a filename for the blob
    const filename = `recording_${new Date().getTime()}.wav`;
    formData.append('audio_file', blob, filename);

    try {
        const response = await fetch('/api/voice/analyze', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            displayVoiceResults(data);
        } else {
            alert('Error: ' + (data.detail || 'Analysis failed'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to analyze voice recording. Please try again.');
    } finally {
        hideLoading();
    }
}

function displayVoiceResults(data) {
    voiceResults.classList.remove('hidden');

    // Display tone
    document.getElementById('voice-tone').textContent = data.tone;

    // Display emotion
    document.getElementById('voice-emotion').textContent = data.emotion;

    // Display risk level
    const riskElement = document.getElementById('voice-risk');
    riskElement.textContent = data.risk_level;
    riskElement.className = `result-value risk-badge risk-${data.risk_level}`;

    // Display stress level
    document.getElementById('voice-stress').textContent =
        `${(data.stress_level * 100).toFixed(1)}%`;

    // Display features
    const featuresGrid = document.getElementById('voice-features');
    featuresGrid.innerHTML = '';

    const features = {
        'Pitch': data.features.pitch,
        'Volume': data.features.volume,
        'Speech Rate': data.features.speech_rate,
        'Energy': data.features.energy
    };

    Object.entries(features).forEach(([label, feature]) => {
        let displayValue = feature;

        // Handle object features (Pitch, Volume, etc.)
        if (typeof feature === 'object' && feature !== null) {
            if (feature.level) {
                // Capitalize level
                displayValue = feature.level.charAt(0).toUpperCase() + feature.level.slice(1);
            } else if (feature.mean !== undefined) {
                displayValue = feature.mean.toFixed(2);
            }
        }

        const featureDiv = document.createElement('div');
        featureDiv.className = 'feature-item';
        featureDiv.innerHTML = `
            <span class="feature-label">${label}</span>
            <span class="feature-value">${displayValue}</span>
        `;
        featuresGrid.appendChild(featureDiv);
    });

    // Display interpretation
    document.getElementById('voice-interpretation').textContent = data.interpretation;

    // Display things to avoid
    const avoidList = document.getElementById('voice-avoid');
    avoidList.innerHTML = '';
    if (data.advice && data.advice.things_to_avoid) {
        data.advice.things_to_avoid.forEach(item => {
            const li = document.createElement('li');
            li.textContent = item;
            avoidList.appendChild(li);
        });
    }

    // Display suggested replies
    const repliesGrid = document.getElementById('voice-replies');
    repliesGrid.innerHTML = '';
    if (data.suggested_replies) {
        data.suggested_replies.forEach(reply => {
            const replyDiv = document.createElement('div');
            replyDiv.className = 'reply-option';
            replyDiv.textContent = reply;
            replyDiv.addEventListener('click', () => {
                navigator.clipboard.writeText(reply);
                alert('Reply copied to clipboard!');
            });
            repliesGrid.appendChild(replyDiv);
        });
    }

    voiceResults.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// ==================== FACE ANALYZER ====================

const faceUpload = document.getElementById('face-upload');
const faceUploadBtn = document.getElementById('face-upload-btn');
const analyzeFaceBtn = document.getElementById('analyze-face-btn');
const facePreview = document.getElementById('face-preview');
const faceResults = document.getElementById('face-results');

// New Camera Elements
const useCameraBtn = document.getElementById('use-camera-btn');
const cameraContainer = document.getElementById('camera-container');
const cameraFeed = document.getElementById('camera-feed');
const cameraCanvas = document.getElementById('camera-canvas');
const captureBtn = document.getElementById('capture-btn');

let selectedFaceFile = null;
let cameraStream = null;

faceUploadBtn.addEventListener('click', () => {
    faceUpload.click();
});

faceUpload.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        selectedFaceFile = file;

        // Show preview
        const reader = new FileReader();
        reader.onload = (e) => {
            facePreview.innerHTML = `<img src="${e.target.result}" alt="Face Preview">`;
            facePreview.classList.remove('hidden');
        };
        reader.readAsDataURL(file);

        analyzeFaceBtn.classList.remove('hidden');
    }
});

analyzeFaceBtn.addEventListener('click', async () => {
    if (!selectedFaceFile) {
        alert('Please select an image first');
        return;
    }

    showLoading();

    const formData = new FormData();
    formData.append('image_file', selectedFaceFile);

    try {
        const response = await fetch('/api/face/analyze', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            displayFaceResults(data);
        } else {
            alert('Error: ' + (data.detail || 'Analysis failed'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to analyze face. Please try again.');
    } finally {
        hideLoading();
    }
});

// --- Camera Logic ---

if (useCameraBtn) {
    useCameraBtn.addEventListener('click', async () => {
        console.log("Use Camera button clicked");

        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            alert("Your browser does not support camera access. Please use a modern browser and ensure you are on HTTPS or localhost.");
            return;
        }

        try {
            console.log("Requesting camera access...");
            cameraStream = await navigator.mediaDevices.getUserMedia({ video: true });
            console.log("Camera access granted");
            cameraFeed.srcObject = cameraStream;

            // UI Updates
            useCameraBtn.classList.add('hidden');
            faceUploadBtn.parentElement.classList.add('hidden'); // Hide upload section
            cameraContainer.classList.remove('hidden');
            faceResults.classList.add('hidden');
            facePreview.classList.add('hidden');
            analyzeFaceBtn.classList.add('hidden');
            selectedFaceFile = null;

        } catch (err) {
            console.error('Error accessing camera:', err);
            alert('Could not access camera: ' + err.message + '. Please ensure you have granted permission.');
        }
    });
} else {
    console.error("Use Camera button not found in DOM");
}

captureBtn.addEventListener('click', () => {
    if (!cameraStream) return;

    // Set canvas dimensions to match video
    cameraCanvas.width = cameraFeed.videoWidth;
    cameraCanvas.height = cameraFeed.videoHeight;

    // Draw current frame
    const context = cameraCanvas.getContext('2d');
    context.drawImage(cameraFeed, 0, 0, cameraCanvas.width, cameraCanvas.height);

    // Convert to blob and analyze
    cameraCanvas.toBlob(async (blob) => {
        await analyzeFaceBlob(blob);

        // Stop camera
        stopCamera();
    }, 'image/jpeg', 0.95);
});

function stopCamera() {
    if (cameraStream) {
        cameraStream.getTracks().forEach(track => track.stop());
        cameraStream = null;
    }

    // UI Updates
    cameraContainer.classList.add('hidden');
    useCameraBtn.classList.remove('hidden');
    faceUploadBtn.parentElement.classList.remove('hidden');
}

async function analyzeFaceBlob(blob) {
    showLoading();

    const formData = new FormData();
    // Create a filename for the blob
    const filename = `capture_${new Date().getTime()}.jpg`;
    formData.append('image_file', blob, filename);

    try {
        const response = await fetch('/api/face/analyze', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            displayFaceResults(data);

            // Show captured image as preview
            const imageUrl = URL.createObjectURL(blob);
            facePreview.innerHTML = `<img src="${imageUrl}" alt="Captured Face">`;
            facePreview.classList.remove('hidden');

        } else {
            alert('Error: ' + (data.detail || 'Analysis failed'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to analyze captured face. Please try again.');
    } finally {
        hideLoading();
    }
}

function displayFaceResults(data) {
    if (!data.face_detected) {
        alert('No face detected in the image. Please upload a clear photo showing your face.');
        return;
    }

    faceResults.classList.remove('hidden');

    // Display emotion
    document.getElementById('face-emotion').textContent = data.emotion;

    // Display risk level
    const riskElement = document.getElementById('face-risk');
    riskElement.textContent = data.risk_level;
    riskElement.className = `result-value risk-badge risk-${data.risk_level}`;

    // Display confidence
    document.getElementById('face-confidence').textContent =
        `${(data.confidence * 100).toFixed(1)}%`;

    // Display emotion breakdown
    const emotionsGrid = document.getElementById('face-emotions');
    emotionsGrid.innerHTML = '';

    Object.entries(data.detailed_emotions).forEach(([emotion, score]) => {
        const emotionDiv = document.createElement('div');
        emotionDiv.className = 'feature-item';
        emotionDiv.innerHTML = `
            <span class="feature-label">${emotion}</span>
            <span class="feature-value">${(score * 100).toFixed(1)}%</span>
        `;
        emotionsGrid.appendChild(emotionDiv);
    });

    faceResults.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// ==================== DASHBOARD ====================

async function loadDashboard() {
    showLoading();

    try {
        const response = await fetch('/api/analysis/dashboard');
        const data = await response.json();

        if (response.ok) {
            displayDashboard(data);
        } else {
            console.error('Failed to load dashboard');
        }
    } catch (error) {
        console.error('Error loading dashboard:', error);
    } finally {
        hideLoading();
    }
}

function displayDashboard(data) {
    // Display stats
    document.getElementById('total-analyses').textContent = data.total_analyses;

    const trendStatus = document.getElementById('trend-status');
    const trend = data.trend.trend;
    trendStatus.textContent = trend.replace('_', ' ').toUpperCase();

    if (trend === 'escalating') {
        trendStatus.style.color = 'var(--danger)';
    } else if (trend === 'improving') {
        trendStatus.style.color = 'var(--success)';
    } else {
        trendStatus.style.color = 'var(--info)';
    }

    // Display risk distribution
    const riskDistribution = document.getElementById('risk-distribution');
    riskDistribution.innerHTML = '';

    const riskColors = {
        'LOW': 'var(--risk-low)',
        'MEDIUM': 'var(--risk-medium)',
        'HIGH': 'var(--risk-high)',
        'CRITICAL': 'var(--risk-critical)'
    };

    const totalRisk = Object.values(data.risk_distribution).reduce((a, b) => a + b, 0);

    Object.entries(data.risk_distribution).forEach(([level, count]) => {
        const percentage = totalRisk > 0 ? (count / totalRisk * 100) : 0;

        const barItem = document.createElement('div');
        barItem.className = 'bar-item';
        barItem.innerHTML = `
            <span class="bar-label">${level}</span>
            <div class="bar-container">
                <div class="bar-fill" style="width: ${percentage}%; background: ${riskColors[level]}">
                    ${count}
                </div>
            </div>
        `;
        riskDistribution.appendChild(barItem);
    });

    // Display emotion distribution
    const emotionDistribution = document.getElementById('emotion-distribution');
    emotionDistribution.innerHTML = '';

    const totalEmotions = Object.values(data.emotion_distribution).reduce((a, b) => a + b, 0);

    Object.entries(data.emotion_distribution).forEach(([emotion, count]) => {
        const percentage = totalEmotions > 0 ? (count / totalEmotions * 100) : 0;

        const barItem = document.createElement('div');
        barItem.className = 'bar-item';
        barItem.innerHTML = `
            <span class="bar-label" style="text-transform: capitalize">${emotion}</span>
            <div class="bar-container">
                <div class="bar-fill" style="width: ${percentage}%; background: var(--primary)">
                    ${count}
                </div>
            </div>
        `;
        emotionDistribution.appendChild(barItem);
    });

    // Display recent history
    const recentHistory = document.getElementById('recent-history');
    recentHistory.innerHTML = '';

    data.recent_analyses.forEach(analysis => {
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';

        const date = new Date(analysis.timestamp).toLocaleString();
        const riskClass = `risk-${analysis.risk_level}`;

        historyItem.innerHTML = `
            <div class="history-item-header">
                <span>
                    <strong>${analysis.type.toUpperCase()}</strong> - 
                    <span style="text-transform: capitalize">${analysis.emotion}</span>
                </span>
                <span class="risk-badge ${riskClass}" style="font-size: 0.8rem; padding: 0.25rem 0.5rem;">
                    ${analysis.risk_level}
                </span>
            </div>
            <div class="history-item-time">${date}</div>
        `;

        recentHistory.appendChild(historyItem);
    });
}

// ==================== INITIALIZATION ====================

// Load dashboard on page load if it's the active tab
document.addEventListener('DOMContentLoaded', () => {
    const dashboardTab = document.getElementById('dashboard-tab');
    if (dashboardTab.classList.contains('active')) {
        loadDashboard();
    }
});
