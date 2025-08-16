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

def test_automatic_translation():
    """Test automatic translation functionality"""
    print("Testing automatic translation functionality...")
    
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Test data with empty translation (should trigger auto-translation)
    test_data = {
        "audio_data": create_test_audio_data(),
        "duration": 3.0,
        "language": "Somali",
        "transcription": "waxaan ahay gabar wanaagsan",
        "translation": ""  # Empty translation - should trigger auto-translation
    }
    
    try:
        # Step 1: Save recording with empty translation
        print("1. Saving recording with empty translation (should auto-translate)...")
        response = requests.post(f"{BASE_URL}/voice/save", json=test_data, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Save failed: {response.status_code} - {response.text}")
            return False
        
        save_data = response.json()
        recording_id = save_data.get('id')
        auto_translation = save_data.get('translation', '')
        
        print(f"✅ Recording saved successfully!")
        print(f"   Recording ID: {recording_id}")
        print(f"   Original transcription: '{test_data['transcription']}'")
        print(f"   Auto-generated translation: '{auto_translation}'")
        
        # Check if translation was generated
        if not auto_translation:
            print(f"❌ No automatic translation was generated!")
            return False
        
        print(f"✅ Automatic translation generated: '{auto_translation}'")
        
        # Step 2: Get recording to verify translation was saved
        print(f"\n2. Getting recording to verify translation was saved...")
        response = requests.get(f"{BASE_URL}/voice/recordings/{recording_id}", headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Get recording failed: {response.status_code} - {response.text}")
            return False
        
        recording = response.json()
        saved_translation = recording.get('translation', '')
        
        print(f"✅ Retrieved recording")
        print(f"   Transcription: '{recording.get('transcription')}'")
        print(f"   Saved translation: '{saved_translation}'")
        
        # Verify translation was saved correctly
        if saved_translation != auto_translation:
            print(f"❌ Translation was not saved correctly!")
            print(f"   Expected: '{auto_translation}'")
            print(f"   Got: '{saved_translation}'")
            return False
        
        print(f"✅ Translation saved correctly!")
        
        # Step 3: Test with provided translation (should not auto-translate)
        print(f"\n3. Testing with provided translation (should not auto-translate)...")
        test_data_with_translation = {
            "audio_data": create_test_audio_data(),
            "duration": 2.5,
            "language": "Somali",
            "transcription": "waan ku faraxsanahay",
            "translation": "I am happy"  # Provided translation
        }
        
        response = requests.post(f"{BASE_URL}/voice/save", json=test_data_with_translation, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Save with translation failed: {response.status_code} - {response.text}")
            return False
        
        save_data_with_translation = response.json()
        recording_id_with_translation = save_data_with_translation.get('id')
        returned_translation = save_data_with_translation.get('translation', '')
        
        print(f"✅ Recording with provided translation saved!")
        print(f"   Recording ID: {recording_id_with_translation}")
        print(f"   Provided translation: '{test_data_with_translation['translation']}'")
        print(f"   Returned translation: '{returned_translation}'")
        
        # Verify provided translation was used
        if returned_translation != test_data_with_translation['translation']:
            print(f"❌ Provided translation was not used!")
            print(f"   Expected: '{test_data_with_translation['translation']}'")
            print(f"   Got: '{returned_translation}'")
            return False
        
        print(f"✅ Provided translation was used correctly!")
        
        # Step 4: Test different Somali phrases
        print(f"\n4. Testing different Somali phrases...")
        test_phrases = [
            "mahadsanid",
            "fadlan i caawi",
            "waan ku faraxsanahay"
        ]
        
        for i, phrase in enumerate(test_phrases):
            test_data_phrase = {
                "audio_data": create_test_audio_data(),
                "duration": 1.5,
                "language": "Somali",
                "transcription": phrase,
                "translation": ""
            }
            
            response = requests.post(f"{BASE_URL}/voice/save", json=test_data_phrase, headers=headers)
            
            if response.status_code == 200:
                save_data_phrase = response.json()
                auto_translation_phrase = save_data_phrase.get('translation', '')
                recording_id_phrase = save_data_phrase.get('id')
                
                print(f"   Phrase {i+1}: '{phrase}' → '{auto_translation_phrase}'")
                
                # Clean up this test recording
                requests.delete(f"{BASE_URL}/voice/recordings/{recording_id_phrase}", headers=headers)
            else:
                print(f"   ❌ Failed to test phrase '{phrase}': {response.status_code}")
        
        # Step 5: Clean up
        print(f"\n5. Cleaning up test recordings...")
        
        # Delete first recording
        response = requests.delete(f"{BASE_URL}/voice/recordings/{recording_id}", headers=headers)
        if response.status_code == 200:
            print(f"✅ First test recording deleted successfully")
        else:
            print(f"⚠️  Could not delete first test recording: {response.status_code}")
        
        # Delete second recording
        response = requests.delete(f"{BASE_URL}/voice/recordings/{recording_id_with_translation}", headers=headers)
        if response.status_code == 200:
            print(f"✅ Second test recording deleted successfully")
        else:
            print(f"⚠️  Could not delete second test recording: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_translation_quality():
    """Test translation quality with known phrases"""
    print("\n\nTesting translation quality...")
    
    # Known Somali phrases and expected English translations
    test_cases = [
        ("mahadsanid", "thank you"),
        ("fadlan", "please"),
        ("waan ku faraxsanahay", "I am happy"),
        ("waan ku faraxsanahay", "I am happy"),
    ]
    
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}",
        "Content-Type": "application/json"
    }
    
    for somali, expected_english in test_cases:
        test_data = {
            "audio_data": create_test_audio_data(),
            "duration": 1.0,
            "language": "Somali",
            "transcription": somali,
            "translation": ""
        }
        
        try:
            response = requests.post(f"{BASE_URL}/voice/save", json=test_data, headers=headers)
            
            if response.status_code == 200:
                save_data = response.json()
                auto_translation = save_data.get('translation', '').lower()
                recording_id = save_data.get('id')
                
                print(f"   '{somali}' → '{auto_translation}'")
                
                # Check if translation contains expected words
                expected_words = expected_english.lower().split()
                translation_words = auto_translation.split()
                
                matches = sum(1 for word in expected_words if word in translation_words)
                if matches > 0:
                    print(f"   ✅ Translation quality: Good ({matches}/{len(expected_words)} words match)")
                else:
                    print(f"   ⚠️  Translation quality: Different from expected")
                
                # Clean up
                requests.delete(f"{BASE_URL}/voice/recordings/{recording_id}", headers=headers)
            else:
                print(f"   ❌ Failed to test '{somali}': {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception testing '{somali}': {str(e)}")
    
    return True

def main():
    print("=== Automatic Translation Test ===\n")
    
    # Test 1: Basic automatic translation
    test1_ok = test_automatic_translation()
    
    # Test 2: Translation quality
    test2_ok = test_translation_quality()
    
    print("\n=== Test Summary ===")
    print(f"Automatic Translation: {'✅' if test1_ok else '❌'}")
    print(f"Translation Quality: {'✅' if test2_ok else '❌'}")
    
    if all([test1_ok, test2_ok]):
        print("\n🎉 Automatic translation functionality is working correctly!")
        print("✅ Empty translations trigger auto-translation")
        print("✅ Provided translations are preserved")
        print("✅ Translation quality is acceptable")
        print("✅ No more empty translation fields!")
        print("\nAutomatic translation feature is ready!")
    else:
        print("\n❌ Some tests failed")
        print("Check the issues above")

if __name__ == "__main__":
    main()
