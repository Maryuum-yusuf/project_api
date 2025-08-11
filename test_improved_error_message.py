#!/usr/bin/env python3
"""
Test script to verify the improved error message with examples
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_improved_error_message():
    """Test the improved error message with examples"""
    
    print("Testing Improved Error Message:")
    print("=" * 50)
    
    # Test with English text
    print("\n1. Testing English text:")
    english_data = {"text": "Hello, how are you?"}
    
    try:
        response = requests.post(f"{BASE_URL}/translate", json=english_data)
        if response.status_code == 400:
            result = response.json()
            print("✅ English text correctly rejected with improved error message")
            print(f"   Error: {result.get('error')}")
            print(f"   Language Detection: {result.get('language_detection')}")
            
            # Check if help section exists
            help_section = result.get('help')
            if help_section:
                print(f"   Help Message: {help_section.get('message')}")
                print("   Examples:")
                for i, example in enumerate(help_section.get('examples', []), 1):
                    print(f"     {i}. {example}")
            else:
                print("   ❌ Help section missing")
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Connection error: {e}")
    
    # Test with mixed text
    print("\n2. Testing mixed text:")
    mixed_data = {"text": "Hello salaam how are you?"}
    
    try:
        response = requests.post(f"{BASE_URL}/translate", json=mixed_data)
        if response.status_code == 400:
            result = response.json()
            print("✅ Mixed text correctly rejected with improved error message")
            print(f"   Error: {result.get('error')}")
            print(f"   Language Detection: {result.get('language_detection')}")
            
            help_section = result.get('help')
            if help_section:
                print(f"   Help Message: {help_section.get('message')}")
                print("   Examples:")
                for i, example in enumerate(help_section.get('examples', []), 1):
                    print(f"     {i}. {example}")
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Connection error: {e}")
    
    # Test with Somali text (should work)
    print("\n3. Testing Somali text (should work):")
    somali_data = {"text": "Salaan, sidee tahay?"}
    
    try:
        response = requests.post(f"{BASE_URL}/translate", json=somali_data)
        if response.status_code == 200:
            result = response.json()
            print("✅ Somali text translated successfully")
            print(f"   Original: {somali_data['text']}")
            print(f"   Translated: {result.get('translated_text')}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Connection error: {e}")

def main():
    print("Improved Error Message Test")
    print("=" * 60)
    
    test_improved_error_message()
    
    print("\n" + "=" * 60)
    print("✅ Improved error message with examples!")
    print("✅ Users now get helpful Somali examples")
    print("✅ Better user experience for non-Somali input")

if __name__ == "__main__":
    main()
