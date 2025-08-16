import requests
import json
import base64

# Test configuration
BASE_URL = "http://localhost:5000"

def test_voice_routes_registration():
    """Test if voice routes are properly registered"""
    print("Testing voice routes registration...")
    
    try:
        # Test if the voice routes are accessible
        response = requests.get(f"{BASE_URL}/voice/recordings")
        
        # Should get 401 (Unauthorized) because no token provided
        # This means the route exists and is working
        if response.status_code == 401:
            print("✅ Voice routes are properly registered!")
            print("   - Route /voice/recordings is accessible")
            print("   - Authentication is working (401 Unauthorized)")
            return True
        elif response.status_code == 404:
            print("❌ Voice routes are NOT registered!")
            print("   - Route /voice/recordings not found")
            return False
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask app!")
        print("   - Make sure Flask app is running on http://localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_gridfs_import():
    """Test if GridFS can be imported"""
    print("\n\nTesting GridFS import...")
    
    try:
        import gridfs
        print("✅ GridFS import successful!")
        return True
    except ImportError as e:
        print(f"❌ GridFS import failed: {str(e)}")
        print("   - Run: pip install gridfs")
        return False
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_voice_save_endpoint():
    """Test voice save endpoint structure"""
    print("\n\nTesting voice save endpoint...")
    
    try:
        # Create minimal test data
        test_data = {
            "audio_data": "data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAAA",
            "duration": 1.0,
            "language": "Somali",
            "transcription": "waan ku faraxsanahay",
            "translation": "I am happy"
        }
        
        response = requests.post(f"{BASE_URL}/voice/save", json=test_data)
        
        # Should get 401 (Unauthorized) because no token provided
        if response.status_code == 401:
            print("✅ Voice save endpoint is working!")
            print("   - POST /voice/save is accessible")
            print("   - Authentication is working (401 Unauthorized)")
            return True
        elif response.status_code == 404:
            print("❌ Voice save endpoint not found!")
            return False
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_available_endpoints():
    """Test available voice endpoints"""
    print("\n\nTesting available voice endpoints...")
    
    endpoints = [
        ("GET", "/voice/recordings"),
        ("POST", "/voice/save"),
        ("GET", "/voice/favorites"),
        ("GET", "/voice/recordings/test-id"),
        ("GET", "/voice/recordings/test-id/audio"),
        ("GET", "/voice/recordings/test-id/audio-data"),
        ("GET", "/voice/recordings/test-id/download"),
        ("POST", "/voice/recordings/test-id/save-local"),
        ("POST", "/voice/recordings/test-id/favorite"),
        ("DELETE", "/voice/recordings/test-id")
    ]
    
    working_endpoints = []
    
    for method, endpoint in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}")
            elif method == "POST":
                response = requests.post(f"{BASE_URL}{endpoint}")
            elif method == "DELETE":
                response = requests.delete(f"{BASE_URL}{endpoint}")
            
            # 401 means endpoint exists but needs authentication
            # 404 means endpoint doesn't exist
            if response.status_code == 401:
                working_endpoints.append(f"{method} {endpoint}")
            elif response.status_code == 404:
                print(f"❌ {method} {endpoint} - Not found")
            else:
                print(f"⚠️  {method} {endpoint} - Status: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {method} {endpoint} - Error: {str(e)}")
    
    print(f"\n✅ Working endpoints ({len(working_endpoints)}):")
    for endpoint in working_endpoints:
        print(f"   - {endpoint}")
    
    return len(working_endpoints) > 0

def main():
    print("=== Voice Routes Integration Test ===\n")
    
    # Test 1: GridFS import
    gridfs_ok = test_gridfs_import()
    
    # Test 2: Voice routes registration
    routes_ok = test_voice_routes_registration()
    
    # Test 3: Voice save endpoint
    save_ok = test_voice_save_endpoint()
    
    # Test 4: Available endpoints
    endpoints_ok = test_available_endpoints()
    
    print("\n=== Test Summary ===")
    print(f"GridFS Import: {'✅' if gridfs_ok else '❌'}")
    print(f"Routes Registration: {'✅' if routes_ok else '❌'}")
    print(f"Save Endpoint: {'✅' if save_ok else '❌'}")
    print(f"Available Endpoints: {'✅' if endpoints_ok else '❌'}")
    
    if all([gridfs_ok, routes_ok, save_ok, endpoints_ok]):
        print("\n🎉 All tests passed! Voice routes are properly integrated.")
        print("\nNext steps:")
        print("1. Get a valid JWT token by logging in")
        print("2. Test with actual audio data")
        print("3. Run: python test_voice_gridfs.py")
    else:
        print("\n⚠️  Some tests failed. Check the issues above.")
        print("\nTroubleshooting:")
        print("1. Make sure Flask app is running: python app.py")
        print("2. Install GridFS: pip install gridfs")
        print("3. Check voice_routes.py import in app.py")
        print("4. Verify MongoDB is running")

if __name__ == "__main__":
    main()
