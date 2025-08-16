# Phone-Based Authentication Guide

## Overview

Authentication system-ka cusub wuxuu isticmaalaa **phone number** beddelka email. Waxaad ku daray validation rules-ka soo socda:

1. **Phone Number**: Somali format (252 country code)
2. **Name**: No numbers allowed
3. **Password**: Minimum 6 characters

## Waxa La Beddelay

### Hore (Old)
```python
# Email-based authentication
{
    "full_name": "Ahmed Hassan",
    "email": "ahmed@example.com",
    "password": "123"
}
```

### Hadda (New)
```python
# Phone-based authentication
{
    "full_name": "Ahmed Hassan",
    "phone": "252123456789",
    "password": "123456"
}
```

## Phone Number Validation

### ✅ Valid Formats
```python
# Somali country code formats
"252123456789"      # 252 + 9 digits
"+252123456789"     # +252 + 9 digits

# Local format (automatically converted to 252)
"123456789"         # 9 digits → becomes "252123456789"

# With formatting (automatically cleaned)
"252 123 456 789"   # With spaces
"252-123-456-789"   # With dashes
"(252)123456789"    # With parentheses
```

### ❌ Invalid Formats
```python
"12345678"          # Too short (8 digits)
"1234567890"        # Too long (10 digits)
"123456789a"        # Contains letters
"abc123def"         # Mixed letters and numbers
""                  # Empty
"123"               # Too short
```

## Name Validation

### ✅ Valid Names
```python
"Ahmed Hassan"
"Maryam Ali"
"Mohamed"
"Amina"
"Abdullahi"
"Fatima"
```

### ❌ Invalid Names
```python
"Ahmed123"          # Contains numbers
"Maryam 456"        # Contains numbers
"123Mohamed"        # Starts with numbers
"A"                 # Too short (less than 2 characters)
""                  # Empty
"Ahmed123Hassan"    # Contains numbers
```

## Password Validation

### ✅ Valid Passwords
```python
"123456"            # Exactly 6 characters
"password123"       # More than 6 characters
"abc123def"         # Mixed characters
"somali123"         # Mixed characters
```

### ❌ Invalid Passwords
```python
"12345"             # Too short (5 characters)
"123"               # Too short
"abc"               # Too short
""                  # Empty
```

## API Endpoints

### 1. Register User

**Endpoint**: `POST /register`

**Request Body**:
```json
{
    "full_name": "Ahmed Hassan",
    "phone": "252123456789",
    "password": "123456",
    "role": "user"  // Optional: "user" or "admin"
}
```

**Success Response** (201):
```json
{
    "message": "User registered successfully"
}
```

**Error Responses** (400):
```json
{
    "error": "Name cannot contain numbers"
}
```
```json
{
    "error": "Invalid phone number format. Use Somali format: 252XXXXXXXXX or +252XXXXXXXXX or XXXXXXXXX (9 digits)"
}
```
```json
{
    "error": "Password must be at least 6 characters long"
}
```
```json
{
    "error": "Phone number already exists"
}
```

### 2. Login User

**Endpoint**: `POST /login`

**Request Body**:
```json
{
    "phone": "252123456789",
    "password": "123456"
}
```

**Success Response** (200):
```json
{
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "role": "user",
    "full_name": "Ahmed Hassan"
}
```

**Error Responses** (400/401):
```json
{
    "error": "Invalid phone number format"
}
```
```json
{
    "error": "Invalid phone number or password"
}
```

## Usage Examples

### JavaScript/Frontend

```javascript
// Register user
const registerUser = async (userData) => {
    const response = await fetch('/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            full_name: "Ahmed Hassan",
            phone: "252123456789",
            password: "123456",
            role: "user"
        })
    });
    
    const data = await response.json();
    
    if (response.ok) {
        console.log("✅ User registered successfully!");
    } else {
        console.log("❌ Error:", data.error);
    }
};

// Login user
const loginUser = async (phone, password) => {
    const response = await fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            phone: phone,
            password: password
        })
    });
    
    const data = await response.json();
    
    if (response.ok) {
        console.log("✅ Login successful!");
        localStorage.setItem('token', data.token);
        return data.token;
    } else {
        console.log("❌ Error:", data.error);
        return null;
    }
};
```

### Python

```python
import requests

# Register user
def register_user(full_name, phone, password, role="user"):
    url = "http://localhost:5000/register"
    data = {
        "full_name": full_name,
        "phone": phone,
        "password": password,
        "role": role
    }
    
    response = requests.post(url, json=data)
    
    if response.status_code == 201:
        print("✅ User registered successfully!")
        return True
    else:
        print(f"❌ Error: {response.json()['error']}")
        return False

# Login user
def login_user(phone, password):
    url = "http://localhost:5000/login"
    data = {
        "phone": phone,
        "password": password
    }
    
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        print("✅ Login successful!")
        token = response.json()['token']
        return token
    else:
        print(f"❌ Error: {response.json()['error']}")
        return None

# Usage
register_user("Ahmed Hassan", "252123456789", "123456")
token = login_user("252123456789", "123456")
```

### cURL

```bash
# Register user
curl -X POST "http://localhost:5000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Ahmed Hassan",
    "phone": "252123456789",
    "password": "123456",
    "role": "user"
  }'

# Login user
curl -X POST "http://localhost:5000/login" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "252123456789",
    "password": "123456"
  }'
```

## Database Schema

### Users Collection
```javascript
{
    "_id": ObjectId("..."),
    "full_name": "Ahmed Hassan",
    "phone": "252123456789",        // Changed from email
    "password": "hashed_password",
    "role": "user",                 // "user" or "admin"
    "is_suspended": false,
    "created_at": ISODate("2024-12-01T10:00:00Z")
}
```

## Validation Functions

### Phone Validation
```python
def validate_somali_phone(phone):
    """Validate Somali phone number format"""
    # Remove spaces and special characters
    phone = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Check if it starts with 252 (country code)
    if phone.startswith('252'):
        # Should be 12 digits total (252 + 9 digits)
        if len(phone) == 12 and phone[3:].isdigit():
            return True, phone
    
    # Check if it starts with +252
    if phone.startswith('+252'):
        # Should be 13 digits total (+252 + 9 digits)
        if len(phone) == 13 and phone[4:].isdigit():
            return True, phone
    
    # Check if it's just 9 digits (local format)
    if len(phone) == 9 and phone.isdigit():
        return True, f"252{phone}"
    
    return False, phone
```

### Name Validation
```python
def validate_name(name):
    """Validate name (no numbers allowed)"""
    if not name or len(name.strip()) < 2:
        return False, "Name must be at least 2 characters long"
    
    # Check if name contains numbers
    if re.search(r'\d', name):
        return False, "Name cannot contain numbers"
    
    return True, name.strip()
```

### Password Validation
```python
def validate_password(password):
    """Validate password (minimum 6 characters)"""
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters long"
    
    return True, password
```

## Testing

### Run Tests
```bash
python test_phone_auth.py
```

### Test Results
```
=== Phone-Based Authentication Tests ===

Testing phone number validation...
✅ Valid phone numbers:
  - 252123456789
  - +252123456789
  - 123456789

❌ Invalid phone numbers:
  - 12345678
  - 123456789a
  - abc123def

Testing name validation...
✅ Valid names:
  - Ahmed Hassan
  - Maryam Ali
  - Mohamed

❌ Invalid names:
  - Ahmed123
  - Maryam 456
  - A

Testing password validation...
✅ Valid passwords (6+ characters):
  - 123456 (6 chars)
  - password123 (11 chars)

❌ Invalid passwords (< 6 characters):
  - 12345 (5 chars)
  - 123 (3 chars)
```

## Error Handling

### Common Errors

1. **Invalid Phone Format**:
   ```json
   {
     "error": "Invalid phone number format. Use Somali format: 252XXXXXXXXX or +252XXXXXXXXX or XXXXXXXXX (9 digits)"
   }
   ```

2. **Name Contains Numbers**:
   ```json
   {
     "error": "Name cannot contain numbers"
   }
   ```

3. **Short Password**:
   ```json
   {
     "error": "Password must be at least 6 characters long"
   }
   ```

4. **Phone Already Exists**:
   ```json
   {
     "error": "Phone number already exists"
   }
   ```

5. **Invalid Login**:
   ```json
   {
     "error": "Invalid phone number or password"
   }
   ```

## Migration from Email

### Database Migration
Haddii aad horey u isticmaashay email-based authentication:

1. **Backup database**:
   ```bash
   mongodump --db somali_translator_db
   ```

2. **Update existing users** (if needed):
   ```javascript
   // MongoDB shell
   db.users.updateMany(
     { email: { $exists: true } },
     [
       {
         $set: {
           phone: "$email",  // Temporary: use email as phone
           email: "$$REMOVE"
         }
       }
     ]
   )
   ```

3. **Update indexes**:
   ```javascript
   // Remove email index
   db.users.dropIndex("email_1")
   
   // Add phone index
   db.users.createIndex({ "phone": 1 }, { unique: true })
   ```

### Frontend Migration
```javascript
// Old email-based form
const oldForm = {
    full_name: "Ahmed Hassan",
    email: "ahmed@example.com",
    password: "123"
};

// New phone-based form
const newForm = {
    full_name: "Ahmed Hassan",
    phone: "252123456789",
    password: "123456"
};
```

## Security Considerations

### Phone Number Security
- Phone numbers are stored in plain text (for SMS functionality)
- Consider encryption for sensitive applications
- Implement rate limiting for registration/login

### Password Security
- Passwords are hashed using bcrypt
- Minimum 6 characters enforced
- Consider additional complexity requirements

### Token Security
- JWT tokens expire after 2 hours
- Tokens contain user_id, phone, and role
- Store tokens securely on frontend

## Support

Haddii aad u baahan tahay caawimaad dheeraad ah:
- Check validation rules
- Test with provided examples
- Verify phone number format
- Check API documentation

---

**Phone-based authentication-ka cusub wuxuu si sax ah u shaqeynaya!** 📱✅
