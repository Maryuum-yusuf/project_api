#!/usr/bin/env python3
"""
Test the exact case from the web interface
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_web_interface_case():
    """Test the exact case from the web interface"""
    
    print("Testing Web Interface Case:")
    print("=" * 50)
    
    # Test the exact text from the image: "how are you"
    print("\n1. Testing 'how are you' (English text):")
    english_data = {"text": "how are you"}
    
    try:
        response = requests.post(f"{BASE_URL}/translate", json=english_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 400:
            result = response.json()
            print("✅ Correctly rejected with Somali error message")
            print(f"Error: {result.get('error')}")
            
            help_section = result.get('help')
            if help_section:
                print(f"Help: {help_section.get('message')}")
                print("Examples:")
                for example in help_section.get('examples', []):
                    print(f"  - {example}")
        else:
            print(f"❌ Unexpected response: {response.text}")
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
    
    # Test with proper Somali text
    print("\n2. Testing 'Salaan, sidee tahay?' (Somali text):")
    somali_data = {"text": "Salaan, sidee tahay?"}
    
    try:
        response = requests.post(f"{BASE_URL}/translate", json=somali_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Correctly translated")
            print(f"Original: {somali_data['text']}")
            print(f"Translated: {result.get('translated_text')}")
        else:
            print(f"❌ Unexpected response: {response.text}")
            
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    test_web_interface_case()
