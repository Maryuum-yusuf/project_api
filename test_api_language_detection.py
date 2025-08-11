#!/usr/bin/env python3
"""
Test script for API language detection functionality
"""

import requests
import json
import time

# Test configuration
BASE_URL = "http://localhost:5000"

def test_translation_with_language_detection():
    """Test the translation endpoint with language detection"""
    
    print("Testing Translation API with Language Detection:")
    print("=" * 60)
    
    test_cases = [
        # Somali text - should translate
        ("Salaan, sidee tahay?", "Somali greeting - should translate"),
        ("Waxaan ku jiraa halkan", "Somali sentence - should translate"),
        ("Mahadsanid fadlan", "Somali thank you - should translate"),
        
        # English text - should reject
        ("Hello, how are you?", "English greeting - should reject"),
        ("I am here today", "English sentence - should reject"),
        ("Thank you please", "English thank you - should reject"),
        
        # Mixed text
        ("Hello salaam", "Mixed languages - might accept"),
    ]
    
    for text, description in test_cases:
        print(f"\n{'='*50}")
        print(f"Testing: {description}")
        print(f"Input text: '{text}'")
        
        try:
            response = requests.post(
                f"{BASE_URL}/translate",
                json={"text": text},
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                # Success - text was translated
                result = response.json()
                print("✅ Translation successful!")
                print(f"Original: {result.get('original_text', 'N/A')}")
                print(f"Translated: {result.get('translated_text', 'N/A')}")
                
                if 'language_detection' in result:
                    lang_info = result['language_detection']
                    print(f"Language: {lang_info.get('detected_language')}")
                    print(f"Confidence: {lang_info.get('language_confidence')}")
                    print(f"Method: {lang_info.get('detection_method')}")
                    print(f"Is Somali: {lang_info.get('is_somali')}")
                    
            elif response.status_code == 400:
                # Error - text was rejected
                result = response.json()
                print("❌ Translation rejected!")
                print(f"Error: {result.get('error', 'Unknown error')}")
                
                if 'language_detection' in result:
                    lang_info = result['language_detection']
                    print(f"Language: {lang_info.get('detected_language')}")
                    print(f"Confidence: {lang_info.get('language_confidence')}")
                    print(f"Method: {lang_info.get('detection_method')}")
                    print(f"Is Somali: {lang_info.get('is_somali')}")
            else:
                print(f"❌ Unexpected status code: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to server. Make sure Flask app is running.")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Small delay between requests
        time.sleep(1)

def test_voice_translation_with_language_detection():
    """Test the voice translation endpoint with language detection"""
    
    print("\n\nTesting Voice Translation API with Language Detection:")
    print("=" * 60)
    
    # First, we need to login to get a token
    login_data = {
        "email": "admin@example.com",
        "password": "admin123"
    }
    
    try:
        # Login
        login_response = requests.post(f"{BASE_URL}/login", json=login_data)
        if login_response.status_code != 200:
            print("❌ Login failed - cannot test voice translation")
            return
        
        token = login_response.json().get("token")
        if not token:
            print("❌ No token received from login")
            return
        
        print("✅ Login successful")
        
        # Test cases for voice translation
        test_cases = [
            ("Salaan, sidee tahay?", "Somali voice text - should translate"),
            ("Hello, how are you?", "English voice text - should reject"),
        ]
        
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        for text, description in test_cases:
            print(f"\n{'='*50}")
            print(f"Testing: {description}")
            print(f"Input text: '{text}'")
            
            # Create a simple test audio file (minimal WAV header)
            test_audio_content = b'\x52\x49\x46\x46\x24\x08\x00\x00\x57\x41\x56\x45'
            
            files = {
                'audio': ('test_recording.wav', test_audio_content, 'audio/wav')
            }
            
            data = {
                'original_text': text
            }
            
            try:
                response = requests.post(
                    f"{BASE_URL}/voice/translate",
                    headers=headers,
                    files=files,
                    data=data
                )
                
                print(f"Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print("✅ Voice translation successful!")
                    print(f"Original: {result.get('original_text', 'N/A')}")
                    print(f"Translated: {result.get('translated_text', 'N/A')}")
                    
                    if 'language_detection' in result:
                        lang_info = result['language_detection']
                        print(f"Language: {lang_info.get('detected_language')}")
                        print(f"Confidence: {lang_info.get('language_confidence')}")
                        print(f"Method: {lang_info.get('detection_method')}")
                        print(f"Is Somali: {lang_info.get('is_somali')}")
                        
                elif response.status_code == 400:
                    result = response.json()
                    print("❌ Voice translation rejected!")
                    print(f"Error: {result.get('error', 'Unknown error')}")
                    
                    if 'language_detection' in result:
                        lang_info = result['language_detection']
                        print(f"Language: {lang_info.get('detected_language')}")
                        print(f"Confidence: {lang_info.get('language_confidence')}")
                        print(f"Method: {lang_info.get('detection_method')}")
                        print(f"Is Somali: {lang_info.get('is_somali')}")
                else:
                    print(f"❌ Unexpected status code: {response.status_code}")
                    print(f"Response: {response.text}")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
            
            time.sleep(1)
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure Flask app is running.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_translation_with_language_detection()
    test_voice_translation_with_language_detection()
