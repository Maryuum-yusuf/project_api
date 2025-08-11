from flask import Blueprint, jsonify, request
from routes.language_detection import somali_detector

language_routes = Blueprint("language_routes", __name__)

@language_routes.route("/detect-language", methods=["POST"])
def detect_text_language():
    """
    Detect if the provided text is Somali or not
    """
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({"error": "Text is required"}), 400
    
    text = data['text']
    
    if not text or not text.strip():
        return jsonify({"error": "Text cannot be empty"}), 400
    
    # Detect language
    detection_result = somali_detector.detect_text_language(text)
    
    return jsonify({
        "text": text,
        "language_detection": {
            "detected_language": detection_result['language'],
            "language_confidence": detection_result['confidence'],
            "detection_method": detection_result['method'],
            "is_somali": detection_result['language'] == 'so',
            "language_name": "Somali" if detection_result['language'] == 'so' else "Other"
        }
    })

@language_routes.route("/is-somali", methods=["POST"])
def is_somali_text():
    """
    Simple endpoint to check if text is Somali
    """
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({"error": "Text is required"}), 400
    
    text = data['text']
    confidence_threshold = data.get('confidence_threshold', 0.5)
    
    if not text or not text.strip():
        return jsonify({"error": "Text cannot be empty"}), 400
    
    # Check if text is Somali
    is_somali = somali_detector.is_somali_text(text, confidence_threshold)
    
    return jsonify({
        "text": text,
        "is_somali": is_somali,
        "confidence_threshold": confidence_threshold
    })

@language_routes.route("/analyze-text", methods=["POST"])
def analyze_text():
    """
    Detailed analysis of text for Somali characteristics
    """
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({"error": "Text is required"}), 400
    
    text = data['text']
    
    if not text or not text.strip():
        return jsonify({"error": "Text cannot be empty"}), 400
    
    # Get detailed analysis
    detection_result = somali_detector.detect_text_language(text)
    
    # Count Somali words
    words = text.lower().split()
    somali_word_count = 0
    somali_words_found = []
    
    for word in words:
        clean_word = word.strip('.,!?;:')
        if clean_word in somali_detector.somali_patterns['common_words']:
            somali_word_count += 1
            somali_words_found.append(clean_word)
    
    # Analyze characteristics
    characteristics = somali_detector._analyze_somali_characteristics(text)
    
    return jsonify({
        "text": text,
        "analysis": {
            "detected_language": detection_result['language'],
            "confidence": detection_result['confidence'],
            "method": detection_result['method'],
            "is_somali": detection_result['language'] == 'so',
            "total_words": len(words),
            "somali_words_count": somali_word_count,
            "somali_words_found": somali_words_found,
            "somali_characteristics_score": characteristics,
            "somali_ratio": somali_word_count / len(words) if len(words) > 0 else 0
        }
    })
