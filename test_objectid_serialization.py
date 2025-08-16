import requests
import json
import base64
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

def test_save_and_retrieve():
    """Test saving a recording and retrieving it to check ObjectId serialization"""
    print("Testing ObjectId serialization...")
    
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Test data
    test_data = {
        "audio_data": create_test_audio_data(),
        "duration": 2.0,
        "language": "Somali",
        "transcription": "waan ku faraxsanahay",
        "translation": "I am happy"
    }
    
    try:
        # Step 1: Save recording
        print("1. Saving voice recording...")
        response = requests.post(f"{BASE_URL}/voice/save", json=test_data, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Save failed: {response.status_code} - {response.text}")
            return False
        
        save_data = response.json()
        recording_id = save_data.get('id')
        file_id = save_data.get('file_id')
        
        print(f"✅ Recording saved successfully!")
        print(f"   Recording ID: {recording_id}")
        print(f"   File ID: {file_id}")
        
        # Step 2: Get recordings list
        print("\n2. Getting recordings list...")
        response = requests.get(f"{BASE_URL}/voice/recordings", headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Get recordings failed: {response.status_code} - {response.text}")
            return False
        
        recordings = response.json()
        print(f"✅ Found {len(recordings)} recordings")
        
        # Check ObjectId serialization
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
        
        # Step 3: Get specific recording
        print(f"\n3. Getting specific recording {recording_id}...")
        response = requests.get(f"{BASE_URL}/voice/recordings/{recording_id}", headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Get specific recording failed: {response.status_code} - {response.text}")
            return False
        
        recording = response.json()
        print(f"✅ Retrieved specific recording")
        print(f"   _id: {recording.get('_id')} (type: {type(recording.get('_id')).__name__})")
        print(f"   user_id: {recording.get('user_id')} (type: {type(recording.get('user_id')).__name__})")
        print(f"   file_id: {recording.get('file_id')} (type: {type(recording.get('file_id')).__name__})")
        
        # Step 4: Test JSON serialization
        print(f"\n4. Testing JSON serialization...")
        try:
            json_str = json.dumps(recording, indent=2)
            print(f"✅ JSON serialization successful!")
            print(f"   JSON length: {len(json_str)} characters")
        except Exception as e:
            print(f"❌ JSON serialization failed: {str(e)}")
            return False
        
        # Step 5: Clean up - delete the test recording
        print(f"\n5. Cleaning up test recording...")
        response = requests.delete(f"{BASE_URL}/voice/recordings/{recording_id}", headers=headers)
        
        if response.status_code == 200:
            print(f"✅ Test recording deleted successfully")
        else:
            print(f"⚠️  Could not delete test recording: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_favorites_serialization():
    """Test favorites endpoint ObjectId serialization"""
    print("\n\nTesting favorites endpoint ObjectId serialization...")
    
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/voice/favorites", headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Get favorites failed: {response.status_code} - {response.text}")
            return False
        
        favorites = response.json()
        print(f"✅ Found {len(favorites)} favorite recordings")
        
        for i, recording in enumerate(favorites):
            print(f"\n   Favorite {i+1}:")
            print(f"     _id: {recording.get('_id')} (type: {type(recording.get('_id')).__name__})")
            print(f"     user_id: {recording.get('user_id')} (type: {type(recording.get('user_id')).__name__})")
            print(f"     file_id: {recording.get('file_id')} (type: {type(recording.get('file_id')).__name__})")
            
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
            
            print(f"     ✅ All ObjectIds properly serialized to strings")
        
        return True
        
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def main():
    print("=== ObjectId Serialization Test ===\n")
    
    # Test 1: Save and retrieve
    test1_ok = test_save_and_retrieve()
    
    # Test 2: Favorites serialization
    test2_ok = test_favorites_serialization()
    
    print("\n=== Test Summary ===")
    print(f"Save and Retrieve: {'✅' if test1_ok else '❌'}")
    print(f"Favorites Serialization: {'✅' if test2_ok else '❌'}")
    
    if all([test1_ok, test2_ok]):
        print("\n🎉 All ObjectId serialization tests passed!")
        print("✅ ObjectIds are properly converted to strings")
        print("✅ JSON serialization works correctly")
        print("✅ No more ObjectId serialization errors")
    else:
        print("\n⚠️  Some tests failed. Check the issues above.")
        print("\nTroubleshooting:")
        print("1. Make sure Flask app is running")
        print("2. Check voice_routes.py serialize_recording function")
        print("3. Verify MongoDB connection")
        print("4. Check authentication token")

if __name__ == "__main__":
    main()
