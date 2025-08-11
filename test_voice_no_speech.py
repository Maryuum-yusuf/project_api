#!/usr/bin/env python3
"""
Test script for voice translation without speech recognition
"""

import requests
import json
import os

# Test configuration
BASE_URL = "http://localhost:5000"
TEST_AUDIO_FILE = "test_audio.wav"  # This would be a real audio file in practice

def test_voice_translation_without_speech():
    """Test the voice translation endpoint with provided text"""
    
    print("Testing voice translation without speech recognition...")
    
    # First, we need to login to get a token
    login_data = {
        "email": "admin@example.com",
        "password": "admin123"
    }
    
    try:
        # Login
        login_response = requests.post(f"{BASE_URL}/login", json=login_data)
        if login_response.status_code != 200:
            print(f"Login failed: {login_response.status_code}")
            return
        
        token = login_response.json().get("token")
        if not token:
            print("No token received from login")
            return
        
        print("✅ Login successful")
        
        # Test voice translation with form data
        # Note: In a real test, you would have an actual audio file
        # For this test, we'll just check if the endpoint accepts the correct structure
        
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        # Create a simple test audio file (1 second of silence)
        # In practice, this would be a real audio recording
        test_audio_content = b'\x52\x49\x46\x46\x24\x08\x00\x00\x57\x41\x56\x45'  # Minimal WAV header
        
        files = {
            'audio': ('test_recording.wav', test_audio_content, 'audio/wav')
        }
        
        data = {
            'original_text': 'Salaan, sidee tahay?'  # Somali text
        }
        
        print("Testing voice translation endpoint...")
        print(f"Request data: {data}")
        
        response = requests.post(
            f"{BASE_URL}/voice/translate",
            headers=headers,
            files=files,
            data=data
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Voice translation successful!")
            print(f"Original text: {result.get('original_text')}")
            print(f"Translated text: {result.get('translated_text')}")
            print(f"Audio filename: {result.get('audio_filename')}")
            
            if 'language_detection' in result:
                lang_info = result['language_detection']
                print(f"Language detection: {lang_info.get('detected_language')} ({lang_info.get('language_confidence')} confidence)")
                print(f"Detection method: {lang_info.get('detection_method')}")
        else:
            print(f"❌ Voice translation failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"Response text: {response.text}")
        
        # Test voice history endpoint
        print("\nTesting voice history endpoint...")
        history_response = requests.get(
            f"{BASE_URL}/voice/history",
            headers=headers
        )
        
        if history_response.status_code == 200:
            history_data = history_response.json()
            print(f"✅ Voice history retrieved: {history_data.get('total', 0)} items")
        else:
            print(f"❌ Voice history failed: {history_response.status_code}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure the Flask app is running.")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    test_voice_translation_without_speech()
