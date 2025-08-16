import requests
import json
import base64

# Test configuration
BASE_URL = "http://localhost:5000"
TEST_TOKEN = "your_test_token_here"  # Replace with actual test token

def test_save_voice_recording_somali():
    """Test saving voice recording with Somali transcription"""
    print("Testing save voice recording with Somali transcription...")
    
    # Mock audio data (base64 encoded)
    mock_audio = base64.b64encode(b"mock_audio_data").decode('utf-8')
    
    payload = {
        "audio_data": mock_audio,
        "duration": 5,
        "language": "Somali",
        "transcription": "waan ku faraxsanahay",
        "translation": "I am happy"
    }
    
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(f"{BASE_URL}/voice/save", json=payload, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("✅ Somali transcription test PASSED")
        return response.json().get("id")
    else:
        print("❌ Somali transcription test FAILED")
        return None

def test_save_voice_recording_english():
    """Test saving voice recording with English transcription (should fail)"""
    print("\nTesting save voice recording with English transcription...")
    
    # Mock audio data (base64 encoded)
    mock_audio = base64.b64encode(b"mock_audio_data").decode('utf-8')
    
    payload = {
        "audio_data": mock_audio,
        "duration": 5,
        "language": "Somali",
        "transcription": "I am happy",
        "translation": "Waan ku faraxsanahay"
    }
    
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(f"{BASE_URL}/voice/save", json=payload, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 400 and "Fadlan ku hadal Somali" in response.json().get("error", ""):
        print("✅ English transcription rejection test PASSED")
        return True
    else:
        print("❌ English transcription rejection test FAILED")
        return False

def test_save_voice_recording_missing_transcription():
    """Test saving voice recording without transcription (should fail)"""
    print("\nTesting save voice recording without transcription...")
    
    # Mock audio data (base64 encoded)
    mock_audio = base64.b64encode(b"mock_audio_data").decode('utf-8')
    
    payload = {
        "audio_data": mock_audio,
        "duration": 5,
        "language": "Somali",
        "translation": "I am happy"
        # Missing transcription
    }
    
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(f"{BASE_URL}/voice/save", json=payload, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 400 and "Transcription is required" in response.json().get("error", ""):
        print("✅ Missing transcription test PASSED")
        return True
    else:
        print("❌ Missing transcription test FAILED")
        return False

def test_get_voice_audio_data(recording_id):
    """Test getting voice recording audio data"""
    print(f"\nTesting get voice audio data for recording {recording_id}...")
    
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}"
    }
    
    response = requests.get(f"{BASE_URL}/voice/recordings/{recording_id}/audio-data", headers=headers)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Audio data present: {'audio_data' in data}")
        print(f"Transcription: {data.get('transcription')}")
        print(f"Translation: {data.get('translation')}")
        print("✅ Get voice audio data test PASSED")
        return True
    else:
        print(f"Response: {response.json()}")
        print("❌ Get voice audio data test FAILED")
        return False

def main():
    print("=== Voice API Updated Tests ===\n")
    
    # Test 1: Save with Somali transcription
    recording_id = test_save_voice_recording_somali()
    
    # Test 2: Save with English transcription (should fail)
    test_save_voice_recording_english()
    
    # Test 3: Save without transcription (should fail)
    test_save_voice_recording_missing_transcription()
    
    # Test 4: Get audio data (if recording was saved)
    if recording_id:
        test_get_voice_audio_data(recording_id)
    
    print("\n=== Test Summary ===")
    print("Make sure to replace TEST_TOKEN with a valid token before running tests.")

if __name__ == "__main__":
    main()
