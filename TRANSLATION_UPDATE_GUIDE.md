# Translation Update Guide

## ✅ **Translation Update Feature Added**

Waxaan ku darey **PUT endpoint** si user-ka uu awood u yeesho inuu translation-ka update gareeyo marka uusan horey u sameyn.

## 🔧 **New API Endpoint**

### **PUT /voice/recordings/<recording_id>**

**Description**: Update a voice recording (translation, favorite status)

**Headers**:
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body**:
```json
{
    "translation": "I am a good girl",
    "is_favorite": true
}
```

**Success Response** (200):
```json
{
    "message": "Recording updated successfully",
    "modified_count": 1
}
```

**Error Responses**:
- `400` - No valid fields to update
- `404` - Recording not found
- `403` - Invalid token

## 📋 **Usage Examples**

### **Frontend (JavaScript)**

```javascript
// Update translation
const updateTranslation = async (recordingId, newTranslation) => {
    const response = await fetch(`/voice/recordings/${recordingId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
            translation: newTranslation
        })
    });
    
    if (response.ok) {
        const result = await response.json();
        console.log("✅ Translation updated:", result.message);
        return true;
    } else {
        console.error("❌ Update failed:", await response.text());
        return false;
    }
};

// Update multiple fields
const updateRecording = async (recordingId, updates) => {
    const response = await fetch(`/voice/recordings/${recordingId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(updates)
    });
    
    if (response.ok) {
        const result = await response.json();
        console.log("✅ Recording updated:", result.message);
        return true;
    } else {
        console.error("❌ Update failed:", await response.text());
        return false;
    }
};

// Usage examples
updateTranslation("68a020e5b3c12e8e1d949171", "I am a good girl");

updateRecording("68a020e5b3c12e8e1d949171", {
    translation: "I am a good girl",
    is_favorite: true
});
```

### **Backend (Python)**

```python
import requests

def update_translation(token, recording_id, translation):
    """Update translation for a voice recording"""
    
    url = f"http://localhost:5000/voice/recordings/{recording_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "translation": translation
    }
    
    response = requests.put(url, json=data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Translation updated: {result['message']}")
        return True
    else:
        print(f"❌ Update failed: {response.text}")
        return False

def update_recording_fields(token, recording_id, updates):
    """Update multiple fields for a voice recording"""
    
    url = f"http://localhost:5000/voice/recordings/{recording_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.put(url, json=updates, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Recording updated: {result['message']}")
        return True
    else:
        print(f"❌ Update failed: {response.text}")
        return False

# Usage examples
token = "your_token_here"
recording_id = "68a020e5b3c12e8e1d949171"

# Update translation only
update_translation(token, recording_id, "I am a good girl")

# Update multiple fields
update_recording_fields(token, recording_id, {
    "translation": "I am a good girl",
    "is_favorite": True
})
```

### **cURL**

```bash
# Update translation
curl -X PUT "http://localhost:5000/voice/recordings/68a020e5b3c12e8e1d949171" \
  -H "Authorization: Bearer your_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "translation": "I am a good girl"
  }'

# Update multiple fields
curl -X PUT "http://localhost:5000/voice/recordings/68a020e5b3c12e8e1d949171" \
  -H "Authorization: Bearer your_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "translation": "I am a good girl",
    "is_favorite": true
  }'
```

## 🎯 **What Can Be Updated**

### **Allowed Fields**
- ✅ **`translation`** - Update the translation text
- ✅ **`is_favorite`** - Toggle favorite status

### **Not Allowed**
- ❌ **`transcription`** - Cannot be changed (preserves original)
- ❌ **`audio_data`** - Cannot be changed (preserves original)
- ❌ **`timestamp`** - Cannot be changed (preserves original)
- ❌ **`user_id`** - Cannot be changed (security)

## 🔒 **Security Features**

### **User Isolation**
- Users can only update their own recordings
- Token validation required
- User ID verification

### **Field Validation**
- Only allowed fields can be updated
- Invalid fields are ignored
- Empty request bodies are rejected

### **Data Integrity**
- Original recording data preserved
- Only specified fields updated
- Atomic updates (all or nothing)

## 🧪 **Testing**

### **Run Translation Update Test**
```bash
python test_translation_update.py
```

### **Expected Results**
```
🎉 Translation update functionality is working correctly!
✅ Translation can be updated
✅ Empty translations are handled
✅ Multiple fields can be updated
✅ Invalid updates are properly rejected
```

## 📊 **Example Workflow**

### **1. Save Recording (Empty Translation)**
```json
POST /voice/save
{
    "audio_data": "data:audio/webm;base64,...",
    "duration": 5.26,
    "language": "Somali",
    "transcription": "waxaan ahay gabar wanaagsan",
    "translation": ""
}
```

### **2. Update Translation**
```json
PUT /voice/recordings/68a020e5b3c12e8e1d949171
{
    "translation": "I am a good girl"
}
```

### **3. Verify Update**
```json
GET /voice/recordings/68a020e5b3c12e8e1d949171
{
    "_id": "68a020e5b3c12e8e1d949171",
    "transcription": "waxaan ahay gabar wanaagsan",
    "translation": "I am a good girl",
    "is_favorite": false,
    ...
}
```

## 🎉 **Benefits**

### **User Experience**
- **Flexible translation**: Users can update translations later
- **No data loss**: Original transcription preserved
- **Easy updates**: Simple API calls

### **Data Management**
- **Incremental updates**: Only change what's needed
- **Audit trail**: Original data preserved
- **Validation**: Only allowed fields updated

### **Frontend Integration**
- **Real-time updates**: Immediate feedback
- **Error handling**: Clear error messages
- **Batch updates**: Multiple fields at once

---

**Translation update feature-ka waa la daray!** ✨

Haddii aad u baahan tahay wax kale oo ka dheer, fadlan i sheeg! 🚀
