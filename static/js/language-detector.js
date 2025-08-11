/**
 * Language Detection Component for Somali Translator
 * Detects if text is Somali and provides feedback
 */

class LanguageDetector {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = {
            autoDetect: true,
            showConfidence: true,
            confidenceThreshold: 0.5,
            ...options
        };
        
        this.init();
    }
    
    init() {
        this.createUI();
        this.bindEvents();
    }
    
    createUI() {
        this.container.innerHTML = `
            <div class="language-detector">
                <div class="detector-header">
                    <h3>🌍 Language Detection</h3>
                    <p>Check if your text is Somali</p>
                </div>
                
                <div class="text-input-section">
                    <textarea id="textInput" placeholder="Enter text to detect language..." rows="4"></textarea>
                    <div class="input-controls">
                        <button id="detectBtn" class="detect-btn" type="button">
                            <i class="detect-icon">🔍</i>
                            Detect Language
                        </button>
                        <button id="clearBtn" class="clear-btn" type="button">
                            <i class="clear-icon">🗑️</i>
                            Clear
                        </button>
                    </div>
                </div>
                
                <div class="detection-result" style="display: none;">
                    <div class="result-header">
                        <h4>Detection Result</h4>
                    </div>
                    <div class="result-content">
                        <div class="language-info">
                            <span class="language-label">Language:</span>
                            <span id="detectedLanguage" class="language-value"></span>
                        </div>
                        <div class="confidence-info" style="display: none;">
                            <span class="confidence-label">Confidence:</span>
                            <span id="confidenceValue" class="confidence-value"></span>
                        </div>
                        <div class="method-info">
                            <span class="method-label">Method:</span>
                            <span id="detectionMethod" class="method-value"></span>
                        </div>
                        <div class="somali-indicator">
                            <span id="somaliIndicator" class="indicator"></span>
                        </div>
                    </div>
                </div>
                
                <div class="detailed-analysis" style="display: none;">
                    <div class="analysis-header">
                        <h4>📊 Detailed Analysis</h4>
                    </div>
                    <div class="analysis-content">
                        <div class="word-stats">
                            <div class="stat-item">
                                <span class="stat-label">Total Words:</span>
                                <span id="totalWords" class="stat-value"></span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">Somali Words:</span>
                                <span id="somaliWords" class="stat-value"></span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">Somali Ratio:</span>
                                <span id="somaliRatio" class="stat-value"></span>
                            </div>
                        </div>
                        <div class="found-words">
                            <span class="found-label">Somali Words Found:</span>
                            <div id="foundWords" class="words-list"></div>
                        </div>
                    </div>
                </div>
                
                <div class="error-message" style="display: none;"></div>
            </div>
        `;
        
        this.addStyles();
    }
    
    addStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .language-detector {
                max-width: 600px;
                margin: 20px auto;
                padding: 20px;
                border: 2px solid #e0e0e0;
                border-radius: 12px;
                background: #f9f9f9;
            }
            
            .detector-header {
                text-align: center;
                margin-bottom: 20px;
            }
            
            .detector-header h3 {
                color: #333;
                margin-bottom: 5px;
            }
            
            .detector-header p {
                color: #666;
                margin: 0;
            }
            
            .text-input-section {
                margin-bottom: 20px;
            }
            
            #textInput {
                width: 100%;
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 14px;
                font-family: inherit;
                resize: vertical;
                box-sizing: border-box;
            }
            
            #textInput:focus {
                outline: none;
                border-color: #667eea;
            }
            
            .input-controls {
                display: flex;
                gap: 10px;
                margin-top: 10px;
            }
            
            .detect-btn, .clear-btn {
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 600;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .detect-btn {
                background: #667eea;
                color: white;
                flex: 1;
            }
            
            .detect-btn:hover {
                background: #5a6fd8;
                transform: translateY(-1px);
            }
            
            .clear-btn {
                background: #9e9e9e;
                color: white;
            }
            
            .clear-btn:hover {
                background: #757575;
            }
            
            .detection-result {
                background: white;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 15px;
                border-left: 4px solid #667eea;
            }
            
            .result-header h4 {
                margin: 0 0 10px 0;
                color: #333;
            }
            
            .language-info, .confidence-info, .method-info {
                display: flex;
                justify-content: space-between;
                margin-bottom: 8px;
                padding: 5px 0;
            }
            
            .language-label, .confidence-label, .method-label {
                font-weight: 600;
                color: #555;
            }
            
            .language-value, .confidence-value, .method-value {
                color: #333;
            }
            
            .somali-indicator {
                text-align: center;
                margin-top: 10px;
                padding: 10px;
                border-radius: 6px;
            }
            
            .indicator.somali {
                background: #e8f5e8;
                color: #2e7d32;
                font-weight: 600;
            }
            
            .indicator.not-somali {
                background: #fff3e0;
                color: #f57c00;
                font-weight: 600;
            }
            
            .detailed-analysis {
                background: white;
                border-radius: 8px;
                padding: 15px;
                border-left: 4px solid #4caf50;
            }
            
            .analysis-header h4 {
                margin: 0 0 15px 0;
                color: #333;
            }
            
            .word-stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 10px;
                margin-bottom: 15px;
            }
            
            .stat-item {
                display: flex;
                justify-content: space-between;
                padding: 8px;
                background: #f5f5f5;
                border-radius: 4px;
            }
            
            .stat-label {
                font-weight: 600;
                color: #555;
            }
            
            .stat-value {
                color: #333;
                font-weight: 600;
            }
            
            .found-words {
                margin-top: 10px;
            }
            
            .found-label {
                font-weight: 600;
                color: #555;
                display: block;
                margin-bottom: 8px;
            }
            
            .words-list {
                display: flex;
                flex-wrap: wrap;
                gap: 5px;
            }
            
            .word-tag {
                background: #667eea;
                color: white;
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 600;
            }
            
            .error-message {
                color: #f44336;
                background: #ffebee;
                padding: 10px;
                border-radius: 5px;
                margin-top: 10px;
                text-align: center;
            }
            
            .detect-icon, .clear-icon {
                font-size: 14px;
            }
        `;
        document.head.appendChild(style);
    }
    
    bindEvents() {
        const detectBtn = document.getElementById('detectBtn');
        const clearBtn = document.getElementById('clearBtn');
        const textInput = document.getElementById('textInput');
        
        detectBtn.addEventListener('click', () => this.detectLanguage());
        clearBtn.addEventListener('click', () => this.clearText());
        
        // Auto-detect on input if enabled
        if (this.options.autoDetect) {
            let timeout;
            textInput.addEventListener('input', () => {
                clearTimeout(timeout);
                timeout = setTimeout(() => {
                    if (textInput.value.trim().length > 10) {
                        this.detectLanguage();
                    }
                }, 1000);
            });
        }
    }
    
    async detectLanguage() {
        const textInput = document.getElementById('textInput');
        const text = textInput.value.trim();
        
        if (!text) {
            this.showError('Please enter some text to detect language.');
            return;
        }
        
        try {
            // Show loading state
            const detectBtn = document.getElementById('detectBtn');
            const originalText = detectBtn.innerHTML;
            detectBtn.innerHTML = '<i class="detect-icon">⏳</i> Detecting...';
            detectBtn.disabled = true;
            
            // Call the API
            const response = await fetch('/detect-language', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text: text })
            });
            
            if (!response.ok) {
                throw new Error('Failed to detect language');
            }
            
            const result = await response.json();
            this.displayResult(result);
            
            // Get detailed analysis
            await this.getDetailedAnalysis(text);
            
        } catch (error) {
            this.showError('Error detecting language: ' + error.message);
        } finally {
            // Reset button
            const detectBtn = document.getElementById('detectBtn');
            detectBtn.innerHTML = '<i class="detect-icon">🔍</i> Detect Language';
            detectBtn.disabled = false;
        }
    }
    
    async getDetailedAnalysis(text) {
        try {
            const response = await fetch('/analyze-text', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text: text })
            });
            
            if (response.ok) {
                const result = await response.json();
                this.displayDetailedAnalysis(result.analysis);
            }
        } catch (error) {
            console.error('Error getting detailed analysis:', error);
        }
    }
    
    displayResult(result) {
        const detectionResult = document.querySelector('.detection-result');
        const detailedAnalysis = document.querySelector('.detailed-analysis');
        
        // Update result display
        document.getElementById('detectedLanguage').textContent = 
            result.language_detection.language_name;
        document.getElementById('detectionMethod').textContent = 
            result.language_detection.detection_method;
        
        if (this.options.showConfidence) {
            document.querySelector('.confidence-info').style.display = 'flex';
            document.getElementById('confidenceValue').textContent = 
                Math.round(result.language_detection.language_confidence * 100) + '%';
        }
        
        // Update Somali indicator
        const indicator = document.getElementById('somaliIndicator');
        if (result.language_detection.is_somali) {
            indicator.textContent = '✅ This appears to be Somali text';
            indicator.className = 'indicator somali';
        } else {
            indicator.textContent = '❌ This does not appear to be Somali text';
            indicator.className = 'indicator not-somali';
        }
        
        // Show results
        detectionResult.style.display = 'block';
        detailedAnalysis.style.display = 'block';
        
        // Hide error if any
        document.querySelector('.error-message').style.display = 'none';
    }
    
    displayDetailedAnalysis(analysis) {
        document.getElementById('totalWords').textContent = analysis.total_words;
        document.getElementById('somaliWords').textContent = analysis.somali_words_count;
        document.getElementById('somaliRatio').textContent = 
            Math.round(analysis.somali_ratio * 100) + '%';
        
        // Display found Somali words
        const foundWordsContainer = document.getElementById('foundWords');
        foundWordsContainer.innerHTML = '';
        
        if (analysis.somali_words_found.length > 0) {
            analysis.somali_words_found.forEach(word => {
                const wordTag = document.createElement('span');
                wordTag.className = 'word-tag';
                wordTag.textContent = word;
                foundWordsContainer.appendChild(wordTag);
            });
        } else {
            foundWordsContainer.innerHTML = '<em>No Somali words detected</em>';
        }
    }
    
    clearText() {
        document.getElementById('textInput').value = '';
        document.querySelector('.detection-result').style.display = 'none';
        document.querySelector('.detailed-analysis').style.display = 'none';
        document.querySelector('.error-message').style.display = 'none';
    }
    
    showError(message) {
        const errorDiv = document.querySelector('.error-message');
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        
        // Hide after 5 seconds
        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 5000);
    }
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LanguageDetector;
}
