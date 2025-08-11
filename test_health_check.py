#!/usr/bin/env python3
"""
Test script for health check endpoints
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_health_endpoints():
    """Test both health check endpoints"""
    
    print("Testing Health Check Endpoints:")
    print("=" * 50)
    
    endpoints = [
        "/health",
        "/api/health"
    ]
    
    for endpoint in endpoints:
        print(f"\nTesting {endpoint}:")
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Status: {result.get('status')}")
                print(f"📝 Message: {result.get('message')}")
                print(f"🕒 Timestamp: {result.get('timestamp')}")
                print(f"📦 Version: {result.get('version')}")
            else:
                print(f"❌ Unexpected status code: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to server. Make sure Flask app is running.")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_health_endpoints()
