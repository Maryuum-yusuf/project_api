#!/usr/bin/env python3
"""
Test script for language detection functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from routes.language_detection import somali_detector

def test_language_detection():
    """Test the language detection with various inputs"""
    
    test_cases = [
        # Somali text examples
        ("Salaan, sidee tahay?", "Somali greeting"),
        ("Waxaan ku jiraa halkan", "Somali sentence"),
        ("Mahadsanid fadlan", "Somali thank you"),
        ("Waxaa jira qof halkan", "Somali with common words"),
        ("Maanta waxaan ku jiraa halkan", "Somali with time words"),
        
        # English text examples
        ("Hello, how are you?", "English greeting"),
        ("I am here today", "English sentence"),
        ("Thank you please", "English thank you"),
        ("There is a person here", "English with common words"),
        ("Today I am here", "English with time words"),
        
        # Mixed or unclear text
        ("Hello salaam", "Mixed languages"),
        ("123 456 789", "Numbers only"),
        ("", "Empty text"),
        ("   ", "Whitespace only"),
    ]
    
    print("Testing Language Detection:")
    print("=" * 50)
    
    for text, description in test_cases:
        result = somali_detector.detect_text_language(text)
        
        status = "✅ SOMALI" if result['language'] == 'so' else "❌ NOT SOMALI"
        confidence = f"{result['confidence']:.2f}"
        
        print(f"\nText: '{text}'")
        print(f"Description: {description}")
        print(f"Result: {status}")
        print(f"Confidence: {confidence}")
        print(f"Method: {result['method']}")
        print(f"Language Code: {result['language']}")
        
        # Test the simple boolean check
        is_somali = somali_detector.is_somali_text(text)
        print(f"Simple Check: {'Somali' if is_somali else 'Not Somali'}")

if __name__ == "__main__":
    test_language_detection()
