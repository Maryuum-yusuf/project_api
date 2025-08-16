import requests
import json
import base64

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

def test_serialization_fix():
    """Test that ObjectId serialization is working correctly"""
    print("Testing ObjectId serialization fix...")
    
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Test data
    test_data = {
        "audio_data": create_test_audio_data(),
        "duration": 1.5,
        "language": "Somali",
        "transcription": "waan ku faraxsanahay",
        "translation": "I am happy"
    }
    
    try:
        # Step 1: Save recording
        print("1. Saving test recording...")
        response = requests.post(f"{BASE_URL}/voice/save", json=test_data, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Save failed: {response.status_code} - {response.text}")
            return False
        
        save_data = response.json()
        recording_id = save_data.get('id')
        
        print(f"✅ Recording saved successfully!")
        print(f"   Recording ID: {recording_id}")
        
        # Step 2: Get recordings list
        print("\n2. Testing GET /voice/recordings...")
        response = requests.get(f"{BASE_URL}/voice/recordings", headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Get recordings failed: {response.status_code} - {response.text}")
            return False
        
        recordings = response.json()
        print(f"✅ Found {len(recordings)} recordings")
        
        # Check serialization
        for i, recording in enumerate(recordings):
            print(f"\n   Recording {i+1}:")
            print(f"     _id: {recording.get('_id')} (type: {type(recording.get('_id')).__name__})")
            print(f"     user_id: {recording.get('user_id')} (type: {type(recording.get('user_id')).__name__})")
            print(f"     file_id: {recording.get('file_id')} (type: {type(recording.get('file_id')).__name__})")
            print(f"     timestamp: {recording.get('timestamp')} (type: {type(recording.get('timestamp')).__name__})")
            
            # Verify all IDs are strings
            if not isinstance(recording.get('_id'), str):
                print(f"     ❌ _id is not a string!")
                return False
            if not isinstance(recording.get('user_id'), str):
                print(f"     ❌ user_id is not a string!")
                return False
            if not isinstance(recording.get('file_id'), str):
                print(f"     ❌ file_id is not a string!")
                return False
            if not isinstance(recording.get('timestamp'), str):
                print(f"     ❌ timestamp is not a string!")
                return False
            
            print(f"     ✅ All ObjectIds properly serialized to strings")
        
        # Step 3: Test specific recording
        print(f"\n3. Testing GET /voice/recordings/{recording_id}...")
        response = requests.get(f"{BASE_URL}/voice/recordings/{recording_id}", headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Get specific recording failed: {response.status_code} - {response.text}")
            return False
        
        recording = response.json()
        print(f"✅ Retrieved specific recording")
        print(f"   _id: {recording.get('_id')} (type: {type(recording.get('_id')).__name__})")
        print(f"   user_id: {recording.get('user_id')} (type: {type(recording.get('user_id')).__name__})")
        print(f"   file_id: {recording.get('file_id')} (type: {type(recording.get('file_id')).__name__})")
        
        # Step 4: Test favorites
        print(f"\n4. Testing GET /voice/favorites...")
        response = requests.get(f"{BASE_URL}/voice/favorites", headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Get favorites failed: {response.status_code} - {response.text}")
            return False
        
        favorites = response.json()
        print(f"✅ Found {len(favorites)} favorite recordings")
        
        # Step 5: Test JSON serialization
        print(f"\n5. Testing JSON serialization...")
        try:
            json_str = json.dumps(recordings, indent=2)
            print(f"✅ JSON serialization successful!")
            print(f"   JSON length: {len(json_str)} characters")
        except Exception as e:
            print(f"❌ JSON serialization failed: {str(e)}")
            return False
        
        # Step 6: Clean up
        print(f"\n6. Cleaning up test recording...")
        response = requests.delete(f"{BASE_URL}/voice/recordings/{recording_id}", headers=headers)
        
        if response.status_code == 200:
            print(f"✅ Test recording deleted successfully")
        else:
            print(f"⚠️  Could not delete test recording: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def main():
    print("=== ObjectId Serialization Fix Test ===\n")
    
    success = test_serialization_fix()
    
    print("\n=== Test Summary ===")
    if success:
        print("🎉 ObjectId serialization fix is working correctly!")
        print("✅ All ObjectIds converted to strings")
        print("✅ JSON serialization works")
        print("✅ No more serialization errors")
        print("\nThe fix is working as expected!")
    else:
        print("❌ Some tests failed")
        print("Check the issues above")

if __name__ == "__main__":
    main()
