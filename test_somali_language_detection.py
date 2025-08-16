import requests
import json
import base64

# Test configuration
BASE_URL = "http://localhost:5000"
TEST_TOKEN = "your_test_token_here"  # Replace with actual test token

def test_somali_words():
    """Test various Somali words and phrases"""
    print("Testing Somali language detection...")
    
    # Test cases with Somali words
    test_cases = [
        "Eedda",  # The word that was failing
        "Nin",    # Man
        "Waan ku faraxsanahay",  # I am happy
        "Mahadsanid",  # Thank you
        "Fadlan",  # Please
        "Waxaan",  # I
        "Waxay",   # They
        "Ku",      # To/For
        "La",      # With
        "Iyo",     # And
        "Waa",     # Is/Are
        "Ma",      # Question particle
        "Miyaa",   # Question particle
        "Qof",     # Person
        "Dad",     # People
        "Bulsho",  # Society
        "Wadan",   # Country
        "Dalka",   # The country
        "Carruur", # Children
        "Naag",    # Woman
        "Hadal",   # Speech
        "Cod",     # Voice
        "Qoraal",  # Text
        "Sheeg",   # Tell
        "Dhig",    # Put
        "Samee",   # Do/Make
        "Ka",      # From
        "Iyagoo",  # They (while)
        "Iyada",   # She/Her
    ]
    
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Mock audio data
    mock_audio = base64.b64encode(b"mock_audio_data").decode('utf-8')
    
    results = []
    
    for i, somali_text in enumerate(test_cases):
        print(f"\nTesting: '{somali_text}'")
        
        payload = {
            "audio_data": mock_audio,
            "duration": 3,
            "language": "Somali",
            "transcription": somali_text,
            "translation": f"Translation {i+1}"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/voice/save", json=payload, headers=headers)
            
            if response.status_code == 200:
                print(f"✅ PASSED: '{somali_text}' - Accepted as Somali")
                results.append(("PASSED", somali_text))
            elif response.status_code == 400:
                error_data = response.json()
                if "Fadlan ku hadal Somali" in error_data.get("error", ""):
                    print(f"❌ FAILED: '{somali_text}' - Rejected as non-Somali")
                    results.append(("FAILED", somali_text))
                else:
                    print(f"⚠️  OTHER ERROR: '{somali_text}' - {error_data.get('error')}")
                    results.append(("ERROR", somali_text))
            else:
                print(f"⚠️  HTTP ERROR: '{somali_text}' - Status: {response.status_code}")
                results.append(("HTTP_ERROR", somali_text))
                
        except Exception as e:
            print(f"❌ EXCEPTION: '{somali_text}' - {str(e)}")
            results.append(("EXCEPTION", somali_text))
    
    return results

def test_non_somali_words():
    """Test non-Somali words to ensure they are rejected"""
    print("\n\nTesting non-Somali language detection...")
    
    # Test cases with non-Somali words
    test_cases = [
        "Hello world",  # English
        "Bonjour",      # French
        "Hola",         # Spanish
        "Ciao",         # Italian
        "Hallo",        # German
        "Привет",       # Russian
        "你好",          # Chinese
        "こんにちは",     # Japanese
        "안녕하세요",     # Korean
        "مرحبا",         # Arabic
    ]
    
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Mock audio data
    mock_audio = base64.b64encode(b"mock_audio_data").decode('utf-8')
    
    results = []
    
    for i, non_somali_text in enumerate(test_cases):
        print(f"\nTesting: '{non_somali_text}'")
        
        payload = {
            "audio_data": mock_audio,
            "duration": 3,
            "language": "Somali",
            "transcription": non_somali_text,
            "translation": f"Translation {i+1}"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/voice/save", json=payload, headers=headers)
            
            if response.status_code == 400:
                error_data = response.json()
                if "Fadlan ku hadal Somali" in error_data.get("error", ""):
                    print(f"✅ CORRECTLY REJECTED: '{non_somali_text}' - Non-Somali detected")
                    results.append(("CORRECTLY_REJECTED", non_somali_text))
                else:
                    print(f"⚠️  WRONG ERROR: '{non_somali_text}' - {error_data.get('error')}")
                    results.append(("WRONG_ERROR", non_somali_text))
            elif response.status_code == 200:
                print(f"❌ INCORRECTLY ACCEPTED: '{non_somali_text}' - Should have been rejected")
                results.append(("INCORRECTLY_ACCEPTED", non_somali_text))
            else:
                print(f"⚠️  HTTP ERROR: '{non_somali_text}' - Status: {response.status_code}")
                results.append(("HTTP_ERROR", non_somali_text))
                
        except Exception as e:
            print(f"❌ EXCEPTION: '{non_somali_text}' - {str(e)}")
            results.append(("EXCEPTION", non_somali_text))
    
    return results

def test_mixed_text():
    """Test mixed Somali and non-Somali text"""
    print("\n\nTesting mixed language detection...")
    
    # Test cases with mixed text
    test_cases = [
        "Waan ku faraxsanahay hello",  # Somali + English
        "Hello waan ku faraxsanahay",  # English + Somali
        "Eedda nin",                   # Somali words
        "Eedda hello",                 # Somali + English
        "Hello eedda",                 # English + Somali
    ]
    
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Mock audio data
    mock_audio = base64.b64encode(b"mock_audio_data").decode('utf-8')
    
    results = []
    
    for i, mixed_text in enumerate(test_cases):
        print(f"\nTesting: '{mixed_text}'")
        
        payload = {
            "audio_data": mock_audio,
            "duration": 3,
            "language": "Somali",
            "transcription": mixed_text,
            "translation": f"Translation {i+1}"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/voice/save", json=payload, headers=headers)
            
            if response.status_code == 200:
                print(f"✅ ACCEPTED: '{mixed_text}' - Considered Somali enough")
                results.append(("ACCEPTED", mixed_text))
            elif response.status_code == 400:
                error_data = response.json()
                if "Fadlan ku hadal Somali" in error_data.get("error", ""):
                    print(f"✅ REJECTED: '{mixed_text}' - Not Somali enough")
                    results.append(("REJECTED", mixed_text))
                else:
                    print(f"⚠️  OTHER ERROR: '{mixed_text}' - {error_data.get('error')}")
                    results.append(("ERROR", mixed_text))
            else:
                print(f"⚠️  HTTP ERROR: '{mixed_text}' - Status: {response.status_code}")
                results.append(("HTTP_ERROR", mixed_text))
                
        except Exception as e:
            print(f"❌ EXCEPTION: '{mixed_text}' - {str(e)}")
            results.append(("EXCEPTION", mixed_text))
    
    return results

def main():
    print("=== Somali Language Detection Tests ===\n")
    
    # Test 1: Somali words
    somali_results = test_somali_words()
    
    # Test 2: Non-Somali words
    non_somali_results = test_non_somali_words()
    
    # Test 3: Mixed text
    mixed_results = test_mixed_text()
    
    print("\n=== Test Summary ===")
    
    print("\nSomali Words Test:")
    passed = sum(1 for result, text in somali_results if result == "PASSED")
    failed = sum(1 for result, text in somali_results if result == "FAILED")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    print("\nNon-Somali Words Test:")
    correctly_rejected = sum(1 for result, text in non_somali_results if result == "CORRECTLY_REJECTED")
    incorrectly_accepted = sum(1 for result, text in non_somali_results if result == "INCORRECTLY_ACCEPTED")
    print(f"✅ Correctly Rejected: {correctly_rejected}")
    print(f"❌ Incorrectly Accepted: {incorrectly_accepted}")
    
    print("\nMixed Text Test:")
    accepted = sum(1 for result, text in mixed_results if result == "ACCEPTED")
    rejected = sum(1 for result, text in mixed_results if result == "REJECTED")
    print(f"✅ Accepted: {accepted}")
    print(f"❌ Rejected: {rejected}")
    
    print("\n=== Specific Test Results ===")
    print("Failed Somali words:")
    for result, text in somali_results:
        if result == "FAILED":
            print(f"  - '{text}'")
    
    print("\nIncorrectly accepted non-Somali words:")
    for result, text in non_somali_results:
        if result == "INCORRECTLY_ACCEPTED":
            print(f"  - '{text}'")
    
    print("\nNote: Replace TEST_TOKEN with a valid token before running tests.")

if __name__ == "__main__":
    main()
