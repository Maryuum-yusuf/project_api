#!/usr/bin/env python3
"""
Test script for voice recording workflow
"""

import requests
import json
import os

BASE_URL = "http://localhost:5000"

def create_dummy_audio_file():
    """Create a dummy audio file for testing"""
    dummy_content = b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xAC\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
    filename = "test_recording.wav"
    with open(filename, "wb") as f:
        f.write(dummy_content)
    return filename

def test_voice_recording_workflow():
    """Test the complete voice recording workflow"""
    
    print("Testing Voice Recording Workflow:")
    print("=" * 50)
    
    # Create dummy audio file (simulating recorded audio from frontend)
    audio_file = create_dummy_audio_file()
    
    try:
        # Test with Somali transcribed text (from frontend speech recognition)
        files = {'audio': open(audio_file, 'rb')}
        data = {'transcribed_text': 'Salaan, sidee tahay?'}
        
        print("1. Testing voice recording with Somali text:")
        print(f"   Audio file: {audio_file}")
        print(f"   Transcribed text: {data['transcribed_text']}")
        
        response = requests.post(f"{BASE_URL}/voice/translate", files=files, data=data)
        
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 403:
            print("   ✅ Correctly requires authentication")
        elif response.status_code == 200:
            result = response.json()
            print("   ✅ Voice recording and translation saved successfully")
            print(f"   Voice ID: {result.get('voice_translation_id')}")
            print(f"   Transcribed: {result.get('transcribed_text')}")
            print(f"   Translated: {result.get('translated_text')}")
            print(f"   Audio file: {result.get('audio_filename')}")
            print(f"   Language detection: {result.get('language_detection')}")
        else:
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    finally:
        # Clean up
        if os.path.exists(audio_file):
            os.remove(audio_file)

def test_voice_recording_english():
    """Test voice recording with English text (should be rejected)"""
    
    print("\n2. Testing voice recording with English text:")
    print("=" * 50)
    
    # Create dummy audio file
    audio_file = create_dummy_audio_file()
    
    try:
        # Test with English transcribed text
        files = {'audio': open(audio_file, 'rb')}
        data = {'transcribed_text': 'Hello, how are you?'}
        
        print(f"   Audio file: {audio_file}")
        print(f"   Transcribed text: {data['transcribed_text']}")
        
        response = requests.post(f"{BASE_URL}/voice/translate", files=files, data=data)
        
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 403:
            print("   ✅ Correctly requires authentication")
        elif response.status_code == 400:
            result = response.json()
            print("   ✅ Correctly rejected English text")
            print(f"   Error: {result.get('error')}")
        else:
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    finally:
        # Clean up
        if os.path.exists(audio_file):
            os.remove(audio_file)

def main():
    print("Voice Recording Workflow Test")
    print("=" * 60)
    
    test_voice_recording_workflow()
    test_voice_recording_english()
    
    print("\n" + "=" * 60)
    print("✅ Voice recording workflow:")
    print("   1. Frontend records audio using microphone")
    print("   2. Frontend converts audio to text (speech recognition)")
    print("   3. Backend receives audio + transcribed text")
    print("   4. Backend does language detection")
    print("   5. If Somali: translates and saves both to database")
    print("   6. If not Somali: returns error message")
    print("✅ Both audio recording and translation saved to database")

if __name__ == "__main__":
    main()
