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

def test_translation_update():
    """Test translation update functionality"""
    print("Testing translation update functionality...")
    
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Test data
    test_data = {
        "audio_data": create_test_audio_data(),
        "duration": 2.0,
        "language": "Somali",
        "transcription": "waxaan ahay gabar wanaagsan",
        "translation": ""  # Empty translation initially
    }
    
    try:
        # Step 1: Save recording with empty translation
        print("1. Saving recording with empty translation...")
        response = requests.post(f"{BASE_URL}/voice/save", json=test_data, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Save failed: {response.status_code} - {response.text}")
            return False
        
        save_data = response.json()
        recording_id = save_data.get('id')
        
        print(f"✅ Recording saved successfully!")
        print(f"   Recording ID: {recording_id}")
        print(f"   Initial translation: '{test_data['translation']}'")
        
        # Step 2: Get recording to verify initial state
        print(f"\n2. Getting recording to verify initial state...")
        response = requests.get(f"{BASE_URL}/voice/recordings/{recording_id}", headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Get recording failed: {response.status_code} - {response.text}")
            return False
        
        recording = response.json()
        print(f"✅ Retrieved recording")
        print(f"   Transcription: '{recording.get('transcription')}'")
        print(f"   Translation: '{recording.get('translation')}'")
        
        # Step 3: Update translation
        print(f"\n3. Updating translation...")
        update_data = {
            "translation": "I am a good girl"
        }
        
        response = requests.put(f"{BASE_URL}/voice/recordings/{recording_id}", json=update_data, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Update failed: {response.status_code} - {response.text}")
            return False
        
        update_result = response.json()
        print(f"✅ Translation updated successfully!")
        print(f"   Message: {update_result.get('message')}")
        print(f"   Modified count: {update_result.get('modified_count')}")
        
        # Step 4: Get recording again to verify update
        print(f"\n4. Getting recording to verify update...")
        response = requests.get(f"{BASE_URL}/voice/recordings/{recording_id}", headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Get recording failed: {response.status_code} - {response.text}")
            return False
        
        updated_recording = response.json()
        print(f"✅ Retrieved updated recording")
        print(f"   Transcription: '{updated_recording.get('transcription')}'")
        print(f"   Translation: '{updated_recording.get('translation')}'")
        
        # Verify translation was updated
        if updated_recording.get('translation') != "I am a good girl":
            print(f"❌ Translation was not updated correctly!")
            print(f"   Expected: 'I am a good girl'")
            print(f"   Got: '{updated_recording.get('translation')}'")
            return False
        
        print(f"✅ Translation update verified!")
        
        # Step 5: Test updating with empty translation
        print(f"\n5. Testing update with empty translation...")
        update_data = {
            "translation": ""
        }
        
        response = requests.put(f"{BASE_URL}/voice/recordings/{recording_id}", json=update_data, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Update with empty translation failed: {response.status_code} - {response.text}")
            return False
        
        print(f"✅ Empty translation update successful!")
        
        # Step 6: Test updating multiple fields
        print(f"\n6. Testing update with multiple fields...")
        update_data = {
            "translation": "I am a good girl (updated)",
            "is_favorite": True
        }
        
        response = requests.put(f"{BASE_URL}/voice/recordings/{recording_id}", json=update_data, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Multiple fields update failed: {response.status_code} - {response.text}")
            return False
        
        print(f"✅ Multiple fields update successful!")
        
        # Step 7: Clean up
        print(f"\n7. Cleaning up test recording...")
        response = requests.delete(f"{BASE_URL}/voice/recordings/{recording_id}", headers=headers)
        
        if response.status_code == 200:
            print(f"✅ Test recording deleted successfully")
        else:
            print(f"⚠️  Could not delete test recording: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_invalid_updates():
    """Test invalid update scenarios"""
    print("\n\nTesting invalid update scenarios...")
    
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Test 1: Update non-existent recording
    print("1. Testing update of non-existent recording...")
    update_data = {"translation": "This should fail"}
    
    response = requests.put(f"{BASE_URL}/voice/recordings/nonexistentid", json=update_data, headers=headers)
    
    if response.status_code == 404:
        print(f"✅ Correctly rejected non-existent recording")
    else:
        print(f"❌ Should have returned 404, got: {response.status_code}")
        return False
    
    # Test 2: Update with no valid fields
    print("2. Testing update with no valid fields...")
    update_data = {"invalid_field": "value"}
    
    response = requests.put(f"{BASE_URL}/voice/recordings/nonexistentid", json=update_data, headers=headers)
    
    if response.status_code == 400:
        print(f"✅ Correctly rejected invalid fields")
    else:
        print(f"❌ Should have returned 400, got: {response.status_code}")
        return False
    
    # Test 3: Update with empty request body
    print("3. Testing update with empty request body...")
    update_data = {}
    
    response = requests.put(f"{BASE_URL}/voice/recordings/nonexistentid", json=update_data, headers=headers)
    
    if response.status_code == 400:
        print(f"✅ Correctly rejected empty request body")
    else:
        print(f"❌ Should have returned 400, got: {response.status_code}")
        return False
    
    return True

def main():
    print("=== Translation Update Test ===\n")
    
    # Test 1: Valid translation updates
    test1_ok = test_translation_update()
    
    # Test 2: Invalid update scenarios
    test2_ok = test_invalid_updates()
    
    print("\n=== Test Summary ===")
    print(f"Valid Updates: {'✅' if test1_ok else '❌'}")
    print(f"Invalid Updates: {'✅' if test2_ok else '❌'}")
    
    if all([test1_ok, test2_ok]):
        print("\n🎉 Translation update functionality is working correctly!")
        print("✅ Translation can be updated")
        print("✅ Empty translations are handled")
        print("✅ Multiple fields can be updated")
        print("✅ Invalid updates are properly rejected")
        print("\nTranslation update feature is ready!")
    else:
        print("\n❌ Some tests failed")
        print("Check the issues above")

if __name__ == "__main__":
    main()
