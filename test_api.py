#!/usr/bin/env python3
"""
Test script for Somali Translator API
This script tests all the major endpoints to ensure they're working correctly.
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_translation():
    """Test translation endpoint"""
    print("Testing translation endpoint...")
    
    # Test without authentication
    response = requests.post(f"{BASE_URL}/translate", 
                           json={"text": "Hello, how are you?"})
    print(f"Translation (no auth): {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Translated: {data.get('translated_text', 'N/A')}")
        return data.get('id')
    return None

def test_register():
    """Test user registration"""
    print("\nTesting user registration...")
    
    user_data = {
        "full_name": "Test User",
        "email": "test@example.com",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/register", json=user_data)
    print(f"Register: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"User registered: {data.get('message', 'N/A')}")
        return data.get('token')
    return None

def test_login():
    """Test user login"""
    print("\nTesting user login...")
    
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/login", json=login_data)
    print(f"Login: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Login successful: {data.get('message', 'N/A')}")
        return data.get('token')
    return None

def test_user_history(token):
    """Test user history endpoint"""
    print("\nTesting user history...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/history", headers=headers)
    print(f"User history: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"History items: {len(data.get('translations', []))}")
        
        # Test getting specific translation if available
        if data.get('translations'):
            first_translation = data['translations'][0]
            translation_id = first_translation.get('_id')
            if translation_id:
                response = requests.get(f"{BASE_URL}/history/{translation_id}", headers=headers)
                print(f"Get specific translation: {response.status_code}")

def test_user_favorites(token):
    """Test user favorites endpoint"""
    print("\nTesting user favorites...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/user/favorites", headers=headers)
    print(f"User favorites: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Favorites items: {len(data.get('favorites', []))}")

def test_user_stats(token):
    """Test user stats endpoint"""
    print("\nTesting user stats...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/user/stats", headers=headers)
    print(f"User stats: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Stats: {data}")

def test_add_favorite(token, translation_id):
    """Test adding favorite"""
    print("\nTesting add favorite...")
    
    headers = {"Authorization": f"Bearer {token}"}
    favorite_data = {"id": translation_id}
    
    response = requests.post(f"{BASE_URL}/favorite", 
                           json=favorite_data, headers=headers)
    print(f"Add favorite: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Favorite added: {data.get('message', 'N/A')}")

def test_admin_endpoints():
    """Test admin endpoints (will fail without admin token)"""
    print("\nTesting admin endpoints...")
    
    # Test dashboard
    response = requests.get(f"{BASE_URL}/admin/dashboard")
    print(f"Admin dashboard: {response.status_code}")
    
    # Test analytics
    response = requests.get(f"{BASE_URL}/admin/analytics")
    print(f"Admin analytics: {response.status_code}")

def test_public_endpoints():
    """Test public endpoints"""
    print("\nTesting public endpoints...")
    
    # Test users count
    response = requests.get(f"{BASE_URL}/users/count")
    print(f"Users count: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total users: {data.get('total_users', 'N/A')}")
    
    # Test all users
    response = requests.get(f"{BASE_URL}/users")
    print(f"All users: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Users returned: {len(data)}")

def main():
    """Main test function"""
    print("Starting API tests...")
    print("=" * 50)
    
    # Test translation first
    translation_id = test_translation()
    
    # Test registration and login
    token = test_register()
    if not token:
        token = test_login()
    
    if token:
        # Test authenticated endpoints
        test_user_history(token)
        test_user_favorites(token)
        test_user_stats(token)
        
        if translation_id:
            test_add_favorite(token, translation_id)
    
    # Test public endpoints
    test_public_endpoints()
    
    # Test admin endpoints (will fail without admin token)
    test_admin_endpoints()
    
    print("\n" + "=" * 50)
    print("API tests completed!")

if __name__ == "__main__":
    main()
