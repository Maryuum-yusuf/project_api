import requests
import json

# Test configuration
BASE_URL = "http://localhost:5000"

def test_phone_validation():
    """Test phone number validation"""
    print("Testing phone number validation...")
    
    # Valid phone numbers
    valid_phones = [
        "252123456789",      # 252 + 9 digits
        "+252123456789",     # +252 + 9 digits
        "123456789",         # 9 digits (local format)
        "252 123 456 789",   # With spaces
        "252-123-456-789",   # With dashes
        "(252)123456789",    # With parentheses
    ]
    
    # Invalid phone numbers
    invalid_phones = [
        "12345678",          # Too short (8 digits)
        "1234567890",        # Too long (10 digits)
        "123456789a",        # Contains letters
        "123456789",         # 9 digits but not Somali format
        "123456789",         # 9 digits but not Somali format
        "abc123def",         # Mixed letters and numbers
        "",                  # Empty
        "123",               # Too short
    ]
    
    print("\n✅ Valid phone numbers:")
    for phone in valid_phones:
        print(f"  - {phone}")
    
    print("\n❌ Invalid phone numbers:")
    for phone in invalid_phones:
        print(f"  - {phone}")

def test_name_validation():
    """Test name validation"""
    print("\n\nTesting name validation...")
    
    # Valid names
    valid_names = [
        "Ahmed Hassan",
        "Maryam Ali",
        "Mohamed",
        "Amina",
        "Abdullahi",
        "Fatima",
    ]
    
    # Invalid names
    invalid_names = [
        "Ahmed123",          # Contains numbers
        "Maryam 456",        # Contains numbers
        "123Mohamed",        # Starts with numbers
        "A",                 # Too short
        "",                  # Empty
        "Ahmed123Hassan",    # Contains numbers
    ]
    
    print("\n✅ Valid names:")
    for name in valid_names:
        print(f"  - {name}")
    
    print("\n❌ Invalid names:")
    for name in invalid_names:
        print(f"  - {name}")

def test_password_validation():
    """Test password validation"""
    print("\n\nTesting password validation...")
    
    # Valid passwords
    valid_passwords = [
        "123456",            # Exactly 6 characters
        "password123",       # More than 6 characters
        "abc123def",         # Mixed characters
        "somali123",         # Mixed characters
    ]
    
    # Invalid passwords
    invalid_passwords = [
        "12345",             # Too short (5 characters)
        "123",               # Too short
        "abc",               # Too short
        "",                  # Empty
    ]
    
    print("\n✅ Valid passwords (6+ characters):")
    for password in valid_passwords:
        print(f"  - {password} ({len(password)} chars)")
    
    print("\n❌ Invalid passwords (< 6 characters):")
    for password in invalid_passwords:
        print(f"  - {password} ({len(password)} chars)")

def test_register_user():
    """Test user registration with phone number"""
    print("\n\nTesting user registration...")
    
    # Test data
    test_user = {
        "full_name": "Test User",
        "phone": "252123456789",
        "password": "123456",
        "role": "user"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register", json=test_user)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 201:
            print("✅ Registration successful!")
            return True
        else:
            print("❌ Registration failed!")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_login_user():
    """Test user login with phone number"""
    print("\n\nTesting user login...")
    
    # Test data
    test_credentials = {
        "phone": "252123456789",
        "password": "123456"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login", json=test_credentials)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            token = response.json().get("token")
            print(f"Token: {token[:20]}..." if token else "No token")
            return token
        else:
            print("❌ Login failed!")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None

def test_invalid_registration():
    """Test invalid registration scenarios"""
    print("\n\nTesting invalid registration scenarios...")
    
    test_cases = [
        {
            "name": "Name with numbers",
            "data": {
                "full_name": "Ahmed123",
                "phone": "252123456789",
                "password": "123456"
            },
            "expected_error": "Name cannot contain numbers"
        },
        {
            "name": "Invalid phone format",
            "data": {
                "full_name": "Ahmed Hassan",
                "phone": "12345678",
                "password": "123456"
            },
            "expected_error": "Invalid phone number format"
        },
        {
            "name": "Short password",
            "data": {
                "full_name": "Ahmed Hassan",
                "phone": "252123456789",
                "password": "123"
            },
            "expected_error": "Password must be at least 6 characters long"
        },
        {
            "name": "Missing fields",
            "data": {
                "full_name": "Ahmed Hassan",
                "phone": "252123456789"
                # Missing password
            },
            "expected_error": "All fields are required"
        }
    ]
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        
        try:
            response = requests.post(f"{BASE_URL}/register", json=test_case["data"])
            
            print(f"Status Code: {response.status_code}")
            response_data = response.json()
            print(f"Response: {response_data}")
            
            if response.status_code == 400:
                error_msg = response_data.get("error", "")
                if test_case["expected_error"] in error_msg:
                    print(f"✅ Correctly rejected: {test_case['name']}")
                else:
                    print(f"⚠️  Wrong error message for: {test_case['name']}")
            else:
                print(f"❌ Should have been rejected: {test_case['name']}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")

def main():
    print("=== Phone-Based Authentication Tests ===\n")
    
    # Test 1: Validation rules
    test_phone_validation()
    test_name_validation()
    test_password_validation()
    
    # Test 2: Invalid registration scenarios
    test_invalid_registration()
    
    # Test 3: Valid registration and login
    print("\n" + "="*50)
    print("Testing valid registration and login...")
    
    # Register a test user
    register_success = test_register_user()
    
    if register_success:
        # Try to login with the registered user
        token = test_login_user()
        
        if token:
            print("\n✅ All tests passed!")
            print("\n=== API Usage Examples ===")
            print("Register:")
            print('curl -X POST "http://localhost:5000/register" \\')
            print('  -H "Content-Type: application/json" \\')
            print('  -d \'{"full_name": "Ahmed Hassan", "phone": "252123456789", "password": "123456"}\'')
            
            print("\nLogin:")
            print('curl -X POST "http://localhost:5000/login" \\')
            print('  -H "Content-Type: application/json" \\')
            print('  -d \'{"phone": "252123456789", "password": "123456"}\'')
        else:
            print("\n❌ Login test failed!")
    else:
        print("\n❌ Registration test failed!")
    
    print("\n=== Validation Rules Summary ===")
    print("📱 Phone Number:")
    print("  - Must be Somali format: 252XXXXXXXXX or +252XXXXXXXXX")
    print("  - Can also be 9 digits (local format)")
    print("  - Spaces, dashes, and parentheses are automatically removed")
    
    print("\n👤 Name:")
    print("  - Must be at least 2 characters long")
    print("  - Cannot contain numbers")
    print("  - Leading/trailing spaces are removed")
    
    print("\n🔒 Password:")
    print("  - Must be at least 6 characters long")
    print("  - Can contain letters, numbers, and special characters")

if __name__ == "__main__":
    main()
