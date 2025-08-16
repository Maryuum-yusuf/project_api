import requests
import json
import base64
import os

# Test configuration
BASE_URL = "http://localhost:5000"
TEST_TOKEN = "your_test_token_here"  # Replace with actual test token

def test_download_voice_recording():
    """Test downloading voice recording as WAV file"""
    print("Testing download voice recording...")
    
    # First, get a list of recordings
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}"
    }
    
    response = requests.get(f"{BASE_URL}/voice/recordings", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to get recordings: {response.status_code}")
        return False
    
    recordings = response.json()
    if not recordings:
        print("❌ No recordings found to test download")
        return False
    
    recording_id = recordings[0]["_id"]
    print(f"Testing download for recording: {recording_id}")
    
    # Test download endpoint
    download_response = requests.get(
        f"{BASE_URL}/voice/recordings/{recording_id}/download", 
        headers=headers
    )
    
    print(f"Download Status Code: {download_response.status_code}")
    
    if download_response.status_code == 200:
        # Check if it's actually a WAV file
        content_type = download_response.headers.get('Content-Type')
        content_disposition = download_response.headers.get('Content-Disposition')
        
        print(f"Content-Type: {content_type}")
        print(f"Content-Disposition: {content_disposition}")
        
        # Save the file to test
        filename = f"test_download_{recording_id}.wav"
        with open(filename, "wb") as f:
            f.write(download_response.content)
        
        file_size = len(download_response.content)
        print(f"✅ Download test PASSED - File saved: {filename} ({file_size} bytes)")
        
        # Clean up test file
        if os.path.exists(filename):
            os.remove(filename)
        
        return True
    else:
        print(f"❌ Download test FAILED: {download_response.text}")
        return False

def test_save_local_voice_recording():
    """Test saving voice recording to local file system"""
    print("\nTesting save local voice recording...")
    
    # First, get a list of recordings
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}"
    }
    
    response = requests.get(f"{BASE_URL}/voice/recordings", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to get recordings: {response.status_code}")
        return False
    
    recordings = response.json()
    if not recordings:
        print("❌ No recordings found to test save local")
        return False
    
    recording_id = recordings[0]["_id"]
    print(f"Testing save local for recording: {recording_id}")
    
    # Test save local endpoint
    save_response = requests.post(
        f"{BASE_URL}/voice/recordings/{recording_id}/save-local", 
        headers=headers
    )
    
    print(f"Save Local Status Code: {save_response.status_code}")
    
    if save_response.status_code == 200:
        data = save_response.json()
        print(f"Response: {data}")
        
        # Check if file was actually created
        file_path = data.get("file_path")
        if file_path and os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"✅ Save local test PASSED - File created: {file_path} ({file_size} bytes)")
            
            # Clean up test file
            os.remove(file_path)
            
            # Clean up downloads directory if empty
            downloads_dir = "downloads"
            if os.path.exists(downloads_dir) and not os.listdir(downloads_dir):
                os.rmdir(downloads_dir)
            
            return True
        else:
            print(f"❌ Save local test FAILED - File not created: {file_path}")
            return False
    else:
        print(f"❌ Save local test FAILED: {save_response.text}")
        return False

def test_base64_audio_playback():
    """Test Base64 audio data retrieval for playback"""
    print("\nTesting Base64 audio data retrieval...")
    
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}"
    }
    
    response = requests.get(f"{BASE_URL}/voice/recordings", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to get recordings: {response.status_code}")
        return False
    
    recordings = response.json()
    if not recordings:
        print("❌ No recordings found to test Base64 playback")
        return False
    
    recording_id = recordings[0]["_id"]
    print(f"Testing Base64 data for recording: {recording_id}")
    
    # Test audio-data endpoint
    audio_response = requests.get(
        f"{BASE_URL}/voice/recordings/{recording_id}/audio-data", 
        headers=headers
    )
    
    print(f"Audio Data Status Code: {audio_response.status_code}")
    
    if audio_response.status_code == 200:
        data = audio_response.json()
        
        # Check if audio_data is present and valid Base64
        audio_data = data.get("audio_data")
        if audio_data:
            try:
                # Test Base64 decoding
                audio_bytes = base64.b64decode(audio_data)
                print(f"✅ Base64 audio test PASSED - Audio data: {len(audio_bytes)} bytes")
                print(f"Transcription: {data.get('transcription', 'N/A')}")
                print(f"Translation: {data.get('translation', 'N/A')}")
                return True
            except Exception as e:
                print(f"❌ Base64 audio test FAILED - Invalid Base64: {str(e)}")
                return False
        else:
            print("❌ Base64 audio test FAILED - No audio_data in response")
            return False
    else:
        print(f"❌ Base64 audio test FAILED: {audio_response.text}")
        return False

def test_base64_to_wav_conversion():
    """Test Base64 to WAV conversion functionality"""
    print("\nTesting Base64 to WAV conversion...")
    
    # Create a mock Base64 audio data (minimal WAV file)
    mock_wav_header = b'RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xAC\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
    mock_base64 = base64.b64encode(mock_wav_header).decode('utf-8')
    
    print(f"Mock Base64 length: {len(mock_base64)}")
    
    try:
        # Decode Base64
        decoded_bytes = base64.b64decode(mock_base64)
        
        # Save as WAV file
        test_filename = "test_conversion.wav"
        with open(test_filename, "wb") as f:
            f.write(decoded_bytes)
        
        # Check if file was created and has correct size
        if os.path.exists(test_filename):
            file_size = os.path.getsize(test_filename)
            print(f"✅ Base64 to WAV conversion PASSED - File: {test_filename} ({file_size} bytes)")
            
            # Clean up
            os.remove(test_filename)
            return True
        else:
            print("❌ Base64 to WAV conversion FAILED - File not created")
            return False
            
    except Exception as e:
        print(f"❌ Base64 to WAV conversion FAILED: {str(e)}")
        return False

def main():
    print("=== Voice Base64 Audio Handling Tests ===\n")
    
    # Test 1: Download voice recording
    test1_result = test_download_voice_recording()
    
    # Test 2: Save local voice recording
    test2_result = test_save_local_voice_recording()
    
    # Test 3: Base64 audio data retrieval
    test3_result = test_base64_audio_playback()
    
    # Test 4: Base64 to WAV conversion
    test4_result = test_base64_to_wav_conversion()
    
    print("\n=== Test Summary ===")
    print(f"Download Test: {'✅ PASSED' if test1_result else '❌ FAILED'}")
    print(f"Save Local Test: {'✅ PASSED' if test2_result else '❌ FAILED'}")
    print(f"Base64 Audio Test: {'✅ PASSED' if test3_result else '❌ FAILED'}")
    print(f"Base64 to WAV Test: {'✅ PASSED' if test4_result else '❌ FAILED'}")
    
    print("\n=== Usage Examples ===")
    print("1. Download audio file:")
    print("   GET /voice/recordings/{id}/download")
    print("   → Returns WAV file for download")
    
    print("\n2. Save to local server:")
    print("   POST /voice/recordings/{id}/save-local")
    print("   → Saves WAV file to server's downloads/ folder")
    
    print("\n3. Get Base64 for playback:")
    print("   GET /voice/recordings/{id}/audio-data")
    print("   → Returns JSON with Base64 audio data")
    
    print("\nNote: Replace TEST_TOKEN with a valid token before running tests.")

if __name__ == "__main__":
    main()
