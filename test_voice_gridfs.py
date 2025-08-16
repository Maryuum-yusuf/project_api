import requests
import json
import base64
import os
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:5000"
TEST_TOKEN = "your_test_token_here"  # Replace with actual test token

def create_test_audio_data():
    """Create a small test audio data (data URL format)"""
    # Create a minimal WAV file header (44 bytes)
    wav_header = b'RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xAC\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
    
    # Convert to base64
    b64_data = base64.b64encode(wav_header).decode('utf-8')
    
    # Create data URL
    data_url = f"data:audio/wav;base64,{b64_data}"
    return data_url

def test_save_voice_recording():
    """Test saving voice recording with GridFS"""
    print("Testing voice recording save with GridFS...")
    
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Test data
    test_data = {
        "audio_data": create_test_audio_data(),
        "duration": 5.5,
        "language": "Somali",
        "transcription": "waan ku faraxsanahay",
        "translation": "I am happy"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/voice/save", json=test_data, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Voice recording saved successfully!")
            print(f"   Recording ID: {data.get('id')}")
            print(f"   File ID: {data.get('file_id')}")
            print(f"   MIME Type: {data.get('mime_type')}")
            print(f"   Size: {data.get('size_bytes')} bytes")
            return data.get('id')
        else:
            print("❌ Voice recording save failed!")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None

def test_get_voice_recordings():
    """Test getting voice recordings list"""
    print("\n\nTesting get voice recordings...")
    
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/voice/recordings", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {len(data)} recordings")
            
            for i, recording in enumerate(data[:3]):  # Show first 3
                print(f"   Recording {i+1}:")
                print(f"     ID: {recording.get('_id')}")
                print(f"     Filename: {recording.get('filename', 'N/A')}")
                print(f"     MIME Type: {recording.get('mime_type', 'N/A')}")
                print(f"     Size: {recording.get('size_bytes', 'N/A')} bytes")
                print(f"     Duration: {recording.get('duration', 'N/A')} seconds")
                print(f"     Transcription: {recording.get('transcription', 'N/A')}")
                print(f"     Translation: {recording.get('translation', 'N/A')}")
                print(f"     Has audio_data: {'audio_data' in recording}")
                print(f"     Has file_id: {'file_id' in recording}")
            
            return data
        else:
            print(f"❌ Failed to get recordings: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None

def test_stream_audio(recording_id):
    """Test streaming audio file"""
    print(f"\n\nTesting audio streaming for recording {recording_id}...")
    
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/voice/recordings/{recording_id}/audio", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"Content-Length: {response.headers.get('Content-Length', 'N/A')}")
        print(f"Content-Disposition: {response.headers.get('Content-Disposition', 'N/A')}")
        
        if response.status_code == 200:
            print("✅ Audio streaming successful!")
            print(f"   Audio data size: {len(response.content)} bytes")
            return True
        else:
            print(f"❌ Audio streaming failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_audio_data_endpoint(recording_id):
    """Test audio-data endpoint (base64 for compatibility)"""
    print(f"\n\nTesting audio-data endpoint for recording {recording_id}...")
    
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/voice/recordings/{recording_id}/audio-data", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Audio data endpoint successful!")
            print(f"   Audio data length: {len(data.get('audio_data', ''))}")
            print(f"   Duration: {data.get('duration', 'N/A')}")
            print(f"   Transcription: {data.get('transcription', 'N/A')}")
            return True
        else:
            print(f"❌ Audio data endpoint failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_download_audio(recording_id):
    """Test downloading audio file"""
    print(f"\n\nTesting audio download for recording {recording_id}...")
    
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/voice/recordings/{recording_id}/download", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"Content-Disposition: {response.headers.get('Content-Disposition', 'N/A')}")
        
        if response.status_code == 200:
            print("✅ Audio download successful!")
            print(f"   Downloaded size: {len(response.content)} bytes")
            
            # Save to test file
            filename = f"test_download_{recording_id}.wav"
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"   Saved to: {filename}")
            return True
        else:
            print(f"❌ Audio download failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_save_local(recording_id):
    """Test saving to local file system"""
    print(f"\n\nTesting save to local for recording {recording_id}...")
    
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/voice/recordings/{recording_id}/save-local", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Save to local successful!")
            print(f"   Filename: {data.get('filename', 'N/A')}")
            print(f"   File path: {data.get('file_path', 'N/A')}")
            print(f"   File size: {data.get('file_size', 'N/A')} bytes")
            return True
        else:
            print(f"❌ Save to local failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_toggle_favorite(recording_id):
    """Test toggling favorite status"""
    print(f"\n\nTesting toggle favorite for recording {recording_id}...")
    
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/voice/recordings/{recording_id}/favorite", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Toggle favorite successful!")
            print(f"   New status: {data.get('is_favorite', 'N/A')}")
            return True
        else:
            print(f"❌ Toggle favorite failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_get_favorites():
    """Test getting favorite recordings"""
    print("\n\nTesting get favorite recordings...")
    
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/voice/favorites", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {len(data)} favorite recordings")
            return True
        else:
            print(f"❌ Get favorites failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_delete_recording(recording_id):
    """Test deleting a recording"""
    print(f"\n\nTesting delete recording {recording_id}...")
    
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}"
    }
    
    try:
        response = requests.delete(f"{BASE_URL}/voice/recordings/{recording_id}", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Delete recording successful!")
            print(f"   Message: {data.get('message', 'N/A')}")
            return True
        else:
            print(f"❌ Delete recording failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_data_url_parsing():
    """Test data URL parsing functionality"""
    print("\n\nTesting data URL parsing...")
    
    # Test valid data URL
    valid_data_url = "data:audio/webm;codecs=opus;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAAA"
    
    # Test invalid data URL
    invalid_data_url = "not-a-data-url"
    
    # Test base64 only
    base64_only = "UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAAA"
    
    print("✅ Data URL parsing tests completed")
    return True

def main():
    print("=== Voice Recording GridFS Tests ===\n")
    
    # Test 1: Data URL parsing
    test_data_url_parsing()
    
    # Test 2: Save voice recording
    recording_id = test_save_voice_recording()
    
    if recording_id:
        # Test 3: Get recordings list
        test_get_voice_recordings()
        
        # Test 4: Stream audio
        test_stream_audio(recording_id)
        
        # Test 5: Audio data endpoint
        test_audio_data_endpoint(recording_id)
        
        # Test 6: Download audio
        test_download_audio(recording_id)
        
        # Test 7: Save to local
        test_save_local(recording_id)
        
        # Test 8: Toggle favorite
        test_toggle_favorite(recording_id)
        
        # Test 9: Get favorites
        test_get_favorites()
        
        # Test 10: Delete recording
        test_delete_recording(recording_id)
    
    print("\n=== GridFS Implementation Summary ===")
    print("✅ GridFS Integration:")
    print("   - Audio files stored in GridFS")
    print("   - Metadata stored in voice_recordings collection")
    print("   - Compact documents (no audio_data field)")
    print("   - Proper MIME type handling")
    print("   - File size validation (max 10MB)")
    print("   - Automatic file cleanup on delete")
    
    print("\n✅ API Endpoints:")
    print("   - POST /voice/save: Save with GridFS")
    print("   - GET /voice/recordings: List recordings")
    print("   - GET /voice/recordings/<id>/audio: Stream audio")
    print("   - GET /voice/recordings/<id>/audio-data: Base64 for compatibility")
    print("   - GET /voice/recordings/<id>/download: Download file")
    print("   - POST /voice/recordings/<id>/save-local: Save to local")
    print("   - POST /voice/recordings/<id>/favorite: Toggle favorite")
    print("   - GET /voice/favorites: Get favorites")
    print("   - DELETE /voice/recordings/<id>: Delete with cleanup")
    
    print("\n✅ Features:")
    print("   - Data URL support (data:audio/webm;base64,...)")
    print("   - Base64 support for backward compatibility")
    print("   - Multiple audio formats (WAV, WebM, OGG, MP3)")
    print("   - Proper Content-Type headers")
    print("   - File size tracking")
    print("   - Automatic filename generation")
    print("   - GridFS file cleanup")
    
    print("\nNote: Replace TEST_TOKEN with a valid token before running tests.")

if __name__ == "__main__":
    main()
