/**
 * Voice Recorder Component for Somali Translator
 * Handles microphone recording and audio upload
 */

class VoiceRecorder {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = {
            maxRecordingTime: 60000, // 60 seconds
            audioFormat: 'wav',
            sampleRate: 44100,
            ...options
        };
        
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
        this.recordingStartTime = null;
        this.timerInterval = null;
        
        this.init();
    }
    
    init() {
        this.createUI();
        this.bindEvents();
    }
    
    createUI() {
        this.container.innerHTML = `
            <div class="voice-recorder">
                <div class="recorder-controls">
                    <button id="recordBtn" class="record-btn" type="button">
                        <i class="mic-icon">🎤</i>
                        <span class="btn-text">Record Voice</span>
                    </button>
                    <button id="stopBtn" class="stop-btn" type="button" style="display: none;">
                        <i class="stop-icon">⏹️</i>
                        <span class="btn-text">Stop Recording</span>
                    </button>
                </div>
                
                <div class="recording-status" style="display: none;">
                    <div class="timer">00:00</div>
                    <div class="recording-indicator">
                        <span class="pulse"></span>
                        Recording...
                    </div>
                </div>
                
                <div class="audio-preview" style="display: none;">
                    <audio id="audioPreview" controls></audio>
                    <div class="preview-controls">
                        <button id="saveBtn" class="save-btn" type="button">
                            <i class="save-icon">💾</i>
                            Save & Translate
                        </button>
                        <button id="discardBtn" class="discard-btn" type="button">
                            <i class="discard-icon">🗑️</i>
                            Discard
                        </button>
                    </div>
                </div>
                
                <div class="error-message" style="display: none;"></div>
            </div>
        `;
        
        // Add CSS styles
        this.addStyles();
    }
    
    addStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .voice-recorder {
                max-width: 400px;
                margin: 20px auto;
                padding: 20px;
                border: 2px solid #e0e0e0;
                border-radius: 12px;
                background: #f9f9f9;
            }
            
            .recorder-controls {
                display: flex;
                gap: 10px;
                margin-bottom: 15px;
            }
            
            .record-btn, .stop-btn, .save-btn, .discard-btn {
                padding: 12px 20px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 600;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .record-btn {
                background: #4CAF50;
                color: white;
            }
            
            .record-btn:hover {
                background: #45a049;
                transform: scale(1.05);
            }
            
            .record-btn.recording {
                background: #f44336;
                animation: pulse 1.5s infinite;
            }
            
            .stop-btn {
                background: #f44336;
                color: white;
            }
            
            .stop-btn:hover {
                background: #da190b;
            }
            
            .save-btn {
                background: #2196F3;
                color: white;
            }
            
            .save-btn:hover {
                background: #1976D2;
            }
            
            .discard-btn {
                background: #9e9e9e;
                color: white;
            }
            
            .discard-btn:hover {
                background: #757575;
            }
            
            .recording-status {
                text-align: center;
                margin: 15px 0;
            }
            
            .timer {
                font-size: 24px;
                font-weight: bold;
                color: #f44336;
                margin-bottom: 10px;
            }
            
            .recording-indicator {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
                color: #f44336;
                font-weight: 600;
            }
            
            .pulse {
                width: 12px;
                height: 12px;
                background: #f44336;
                border-radius: 50%;
                animation: pulse 1.5s infinite;
            }
            
            .audio-preview {
                margin-top: 15px;
                text-align: center;
            }
            
            .audio-preview audio {
                width: 100%;
                margin-bottom: 15px;
            }
            
            .preview-controls {
                display: flex;
                gap: 10px;
                justify-content: center;
            }
            
            .error-message {
                color: #f44336;
                background: #ffebee;
                padding: 10px;
                border-radius: 5px;
                margin-top: 10px;
                text-align: center;
            }
            
            @keyframes pulse {
                0% { opacity: 1; transform: scale(1); }
                50% { opacity: 0.5; transform: scale(1.2); }
                100% { opacity: 1; transform: scale(1); }
            }
            
            .mic-icon, .stop-icon, .save-icon, .discard-icon {
                font-size: 16px;
            }
        `;
        document.head.appendChild(style);
    }
    
    bindEvents() {
        const recordBtn = document.getElementById('recordBtn');
        const stopBtn = document.getElementById('stopBtn');
        const saveBtn = document.getElementById('saveBtn');
        const discardBtn = document.getElementById('discardBtn');
        
        recordBtn.addEventListener('click', () => this.startRecording());
        stopBtn.addEventListener('click', () => this.stopRecording());
        saveBtn.addEventListener('click', () => this.saveRecording());
        discardBtn.addEventListener('click', () => this.discardRecording());
    }
    
    async startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    sampleRate: this.options.sampleRate,
                    channelCount: 1,
                    echoCancellation: true,
                    noiseSuppression: true
                } 
            });
            
            this.mediaRecorder = new MediaRecorder(stream, {
                mimeType: 'audio/webm;codecs=opus'
            });
            
            this.audioChunks = [];
            this.isRecording = true;
            this.recordingStartTime = Date.now();
            
            this.mediaRecorder.ondataavailable = (event) => {
                this.audioChunks.push(event.data);
            };
            
            this.mediaRecorder.onstop = () => {
                this.showAudioPreview();
                stream.getTracks().forEach(track => track.stop());
            };
            
            this.mediaRecorder.start();
            this.updateUI('recording');
            this.startTimer();
            
            // Auto-stop after max recording time
            setTimeout(() => {
                if (this.isRecording) {
                    this.stopRecording();
                }
            }, this.options.maxRecordingTime);
            
        } catch (error) {
            this.showError('Microphone access denied. Please allow microphone permissions.');
            console.error('Error accessing microphone:', error);
        }
    }
    
    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
            this.stopTimer();
            this.updateUI('stopped');
        }
    }
    
    startTimer() {
        this.timerInterval = setInterval(() => {
            const elapsed = Date.now() - this.recordingStartTime;
            const seconds = Math.floor(elapsed / 1000);
            const minutes = Math.floor(seconds / 60);
            const remainingSeconds = seconds % 60;
            
            const timerElement = document.querySelector('.timer');
            if (timerElement) {
                timerElement.textContent = `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
            }
        }, 1000);
    }
    
    stopTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
    }
    
    showAudioPreview() {
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
        const audioUrl = URL.createObjectURL(audioBlob);
        
        const audioPreview = document.getElementById('audioPreview');
        audioPreview.src = audioUrl;
        
        document.querySelector('.audio-preview').style.display = 'block';
    }
    
    async saveRecording() {
        const saveBtn = document.getElementById('saveBtn');
        const originalText = saveBtn.querySelector('.btn-text').textContent;
        
        try {
            saveBtn.disabled = true;
            saveBtn.querySelector('.btn-text').textContent = 'Saving...';
            
            // Get transcribed text from options or prompt user
            let transcribedText = this.options.transcribedText;
            if (!transcribedText) {
                transcribedText = prompt('Please enter the transcribed text from your audio recording:');
                if (!transcribedText || transcribedText.trim() === '') {
                    throw new Error('Transcribed text is required');
                }
            }
            
            const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.webm');
            formData.append('original_text', transcribedText);
            
            // Get auth token from localStorage or wherever it's stored
            const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
            
            if (!token) {
                throw new Error('Authentication token not found. Please login first.');
            }
            
            const response = await fetch('/voice/translate', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to save recording');
            }
            
            const result = await response.json();
            
            // Show success message
            this.showSuccess(result);
            
            // Reset recorder
            this.resetRecorder();
            
        } catch (error) {
            this.showError(error.message);
        } finally {
            saveBtn.disabled = false;
            saveBtn.querySelector('.btn-text').textContent = originalText;
        }
    }
    
    showSuccess(result) {
        // Create success message
        const successDiv = document.createElement('div');
        successDiv.className = 'success-message';
        
        // Language detection info
        let languageInfo = '';
        if (result.language_detection) {
            const lang = result.language_detection;
            const isSomali = lang.is_somali;
            const confidence = Math.round(lang.language_confidence * 100);
            
            languageInfo = `
                <div style="background: ${isSomali ? '#e8f5e8' : '#fff3e0'}; color: ${isSomali ? '#2e7d32' : '#f57c00'}; padding: 10px; border-radius: 5px; margin: 10px 0; text-align: center;">
                    <strong>🌍 Language Detection:</strong> ${isSomali ? 'Somali' : 'Other'} (${confidence}% confidence)
                    <br><small>Method: ${lang.detection_method}</small>
                </div>
            `;
        }
        
        successDiv.innerHTML = `
            <div style="background: #e8f5e8; color: #2e7d32; padding: 15px; border-radius: 5px; margin-top: 10px; text-align: center;">
                <h4>✅ Voice Translation Successful!</h4>
                <p><strong>Original:</strong> ${result.original_text}</p>
                <p><strong>Translated:</strong> ${result.translated_text}</p>
                <p><small>Audio saved as: ${result.audio_filename}</small></p>
                ${languageInfo}
            </div>
        `;
        
        this.container.appendChild(successDiv);
        
        // Remove success message after 8 seconds (longer to read language info)
        setTimeout(() => {
            if (successDiv.parentNode) {
                successDiv.parentNode.removeChild(successDiv);
            }
        }, 8000);
    }
    
    discardRecording() {
        this.resetRecorder();
    }
    
    resetRecorder() {
        this.audioChunks = [];
        this.isRecording = false;
        this.stopTimer();
        this.updateUI('idle');
        
        // Clear audio preview
        const audioPreview = document.getElementById('audioPreview');
        if (audioPreview.src) {
            URL.revokeObjectURL(audioPreview.src);
            audioPreview.src = '';
        }
        
        document.querySelector('.audio-preview').style.display = 'none';
        document.querySelector('.error-message').style.display = 'none';
    }
    
    updateUI(state) {
        const recordBtn = document.getElementById('recordBtn');
        const stopBtn = document.getElementById('stopBtn');
        const recordingStatus = document.querySelector('.recording-status');
        
        switch (state) {
            case 'recording':
                recordBtn.style.display = 'none';
                stopBtn.style.display = 'flex';
                recordingStatus.style.display = 'block';
                recordBtn.classList.add('recording');
                break;
                
            case 'stopped':
                recordBtn.style.display = 'flex';
                stopBtn.style.display = 'none';
                recordingStatus.style.display = 'none';
                recordBtn.classList.remove('recording');
                break;
                
            case 'idle':
            default:
                recordBtn.style.display = 'flex';
                stopBtn.style.display = 'none';
                recordingStatus.style.display = 'none';
                recordBtn.classList.remove('recording');
                break;
        }
    }
    
    showError(message) {
        const errorDiv = document.querySelector('.error-message');
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        
        // Hide error after 5 seconds
        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 5000);
    }
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = VoiceRecorder;
}
