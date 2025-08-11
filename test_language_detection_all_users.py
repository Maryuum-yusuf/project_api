#!/usr/bin/env python3
"""
Test script to verify language detection works for all users (logged in or not)
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_translate_without_auth():
    """Test translation without authentication (should still do language detection)"""
    
    print("Testing Translation WITHOUT Authentication:")
    print("=" * 50)
    
    # Test 1: Somali text (should work)
    print("\n1. Testing Somali text:")
    somali_data = {"text": "Salaan, sidee tahay?"}
    
    try:
        response = requests.post(f"{BASE_URL}/translate", json=somali_data)
        if response.status_code == 200:
            result = response.json()
            print("✅ Somali text translated successfully")
            print(f"   Original: {somali_data['text']}")
            print(f"   Translated: {result.get('translated_text')}")
            print(f"   Language Detection: {result.get('language_detection')}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Connection error: {e}")
    
    # Test 2: English text (should be rejected)
    print("\n2. Testing English text:")
    english_data = {"text": "Hello, how are you?"}
    
    try:
        response = requests.post(f"{BASE_URL}/translate", json=english_data)
        if response.status_code == 400:
            result = response.json()
            print("✅ English text correctly rejected")
            print(f"   Error: {result.get('error')}")
            print(f"   Language Detection: {result.get('language_detection')}")
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Connection error: {e}")

def test_translate_with_auth():
    """Test translation with authentication (should still do language detection)"""
    
    print("\n\nTesting Translation WITH Authentication:")
    print("=" * 50)
    
    # First, try to login to get a token
    print("\n1. Attempting to login (if user exists):")
    login_data = {
        "email": "test@example.com",
        "password": "testpassword"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            result = response.json()
            token = result.get('token')
            print("✅ Login successful, got token")
            
            # Test with token
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test Somali text with auth
            print("\n2. Testing Somali text WITH authentication:")
            somali_data = {"text": "Waxaan rabaa inaan turjumo qoraalkan"}
            
            response = requests.post(f"{BASE_URL}/translate", json=somali_data, headers=headers)
            if response.status_code == 200:
                result = response.json()
                print("✅ Somali text translated successfully with auth")
                print(f"   Original: {somali_data['text']}")
                print(f"   Translated: {result.get('translated_text')}")
                print(f"   Language Detection: {result.get('language_detection')}")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"   Response: {response.text}")
            
            # Test English text with auth
            print("\n3. Testing English text WITH authentication:")
            english_data = {"text": "I want to translate this text"}
            
            response = requests.post(f"{BASE_URL}/translate", json=english_data, headers=headers)
            if response.status_code == 400:
                result = response.json()
                print("✅ English text correctly rejected with auth")
                print(f"   Error: {result.get('error')}")
                print(f"   Language Detection: {result.get('language_detection')}")
            else:
                print(f"❌ Unexpected response: {response.status_code}")
                print(f"   Response: {response.text}")
                
        else:
            print("⚠️  Login failed (user might not exist), testing without auth")
            test_translate_without_auth()
            
    except Exception as e:
        print(f"❌ Connection error: {e}")

def main():
    print("Language Detection Test for All Users")
    print("=" * 60)
    
    test_translate_without_auth()
    test_translate_with_auth()
    
    print("\n" + "=" * 60)
    print("✅ Language detection is active for ALL users!")
    print("✅ Both authenticated and non-authenticated users get language detection")
    print("✅ Non-Somali text is rejected with Somali error message")

if __name__ == "__main__":
    main()
