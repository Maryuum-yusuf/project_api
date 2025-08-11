#!/usr/bin/env python3
"""
Test script for Voice Translation API
This script tests the voice translation endpoints.
"""

import requests
import json
import os
import time

BASE_URL = "http://localhost:5000"

def test_voice_translation(token):
    """Test voice translation endpoint"""
    print("Testing voice translation endpoint...")
    
    # Create a simple test audio file (you would normally upload a real audio file)
    # For testing purposes, we'll create a dummy file
    test_audio_path = "test_audio.wav"
    
    # Create a simple WAV file for testing (this is just a placeholder)
    # In real usage, you would upload an actual audio file
    try:
        with open(test_audio_path, 'wb') as f:
            # Write a minimal WAV header (this won't actually be playable)
            f.write(b'RIFF')
            f.write(b'\x24\x00\x00\x00')  # File size
            f.write(b'WAVE')
            f.write(b'fmt ')
            f.write(b'\x10\x00\x00\x00')  # Chunk size
            f.write(b'\x01\x00')          # Audio format (PCM)
            f.write(b'\x01\x00')          # Channels
            f.write(b'\x44\xAC\x00\x00')  # Sample rate
            f.write(b'\x88\x58\x01\x00')  # Byte rate
            f.write(b'\x02\x00')          # Block align
            f.write(b'\x10\x00')          # Bits per sample
            f.write(b'data')
            f.write(b'\x00\x00\x00\x00')  # Data size
        
        headers = {"Authorization": f"Bearer {token}"}
        
        with open(test_audio_path, 'rb') as audio_file:
            files = {'audio': ('test_audio.wav', audio_file, 'audio/wav')}
            response = requests.post(f"{BASE_URL}/voice/translate", 
                                   files=files, headers=headers)
        
        print(f"Voice translation: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Voice translation successful: {data.get('message', 'N/A')}")
            print(f"Original text: {data.get('original_text', 'N/A')}")
            print(f"Translated text: {data.get('translated_text', 'N/A')}")
            return data.get('voice_translation_id')
        else:
            print(f"Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error creating test audio file: {e}")
        return None
    finally:
        # Clean up test file
        if os.path.exists(test_audio_path):
            os.remove(test_audio_path)

def test_voice_history(token):
    """Test voice history endpoint"""
    print("\nTesting voice history...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/voice/history", headers=headers)
    print(f"Voice history: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Voice history items: {len(data.get('voice_translations', []))}")
        return data.get('voice_translations', [])
    return []

def test_get_voice_translation(token, voice_id):
    """Test getting specific voice translation"""
    print(f"\nTesting get voice translation {voice_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/voice/{voice_id}", headers=headers)
    print(f"Get voice translation: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Voice translation details: {data.get('original_text', 'N/A')} -> {data.get('translated_text', 'N/A')}")

def test_download_audio(token, voice_id):
    """Test downloading audio file"""
    print(f"\nTesting download audio for {voice_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/voice/{voice_id}/audio", headers=headers)
    print(f"Download audio: {response.status_code}")
    if response.status_code == 200:
        # Save the downloaded audio file
        filename = f"downloaded_audio_{voice_id}.wav"
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Audio downloaded as: {filename}")
        return filename
    return None

def test_voice_stats(token):
    """Test user stats including voice translations"""
    print("\nTesting user stats with voice data...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/user/stats", headers=headers)
    print(f"User stats: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total voice translations: {data.get('total_voice_translations', 'N/A')}")

def main():
    """Main test function"""
    print("Starting Voice API tests...")
    print("=" * 50)
    
    # First, we need to login to get a token
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/login", json=login_data)
    if response.status_code != 200:
        print("Login failed. Please register a user first or check credentials.")
        return
    
    token = response.json().get('token')
    if not token:
        print("No token received from login.")
        return
    
    print("Login successful!")
    
    # Test voice translation (this will likely fail without a real audio file)
    voice_id = test_voice_translation(token)
    
    # Test voice history
    voice_translations = test_voice_history(token)
    
    # Test getting specific voice translation if available
    if voice_translations:
        first_voice = voice_translations[0]
        voice_id = first_voice.get('_id')
        if voice_id:
            test_get_voice_translation(token, voice_id)
            test_download_audio(token, voice_id)
    
    # Test user stats
    test_voice_stats(token)
    
    print("\n" + "=" * 50)
    print("Voice API tests completed!")
    print("\nNote: Voice translation requires a real audio file with clear speech.")
    print("The test audio file created is not a valid audio file and will fail.")

if __name__ == "__main__":
    main()
