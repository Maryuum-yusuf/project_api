#!/usr/bin/env python3
"""
Simple test to demonstrate the improved error message
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_error_message():
    """Test the improved error message"""
    
    print("Testing Improved Error Message:")
    print("=" * 50)
    
    # Test with English text (should be rejected)
    test_text = "Hello, how are you?"
    
    print(f"Input text: '{test_text}'")
    print("Expected: Should be rejected with clear Somali error message")
    print()
    
    try:
        response = requests.post(
            f"{BASE_URL}/translate",
            json={"text": test_text},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            result = response.json()
            print("✅ Error message received:")
            print(f"Error: {result.get('error')}")
            print()
            print("📝 Error message translation:")
            print("English: 'The text you entered is not Somali language. Please enter Somali text.'")
            print()
            print("🔍 Language detection details:")
            if 'language_detection' in result:
                lang_info = result['language_detection']
                print(f"Detected language: {lang_info.get('detected_language')}")
                print(f"Confidence: {lang_info.get('language_confidence')}")
                print(f"Detection method: {lang_info.get('detection_method')}")
                print(f"Is Somali: {lang_info.get('is_somali')}")
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure Flask app is running.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_error_message()
