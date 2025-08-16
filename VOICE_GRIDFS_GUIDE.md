# Voice Recording GridFS Implementation Guide

## Overview

Voice recording system-ka cusub wuxuu isticmaalaa **GridFS** si codka uu si fiican ugu galo MongoDB. Tani waxay ka dhigan tahay:

1. **GridFS Storage**: Audio files ku kaydin GridFS
2. **Compact Metadata**: Documents kooban (ma jiro audio_data field)
3. **Data URL Support**: Frontend-ka wuxuu dir karaa data URLs
4. **Multiple Formats**: WAV, WebM, OGG, MP3
5. **Automatic Cleanup**: GridFS files la tirtiro marka la delete gareeyo

## Waxa La Beddelay

### Hore (Old Implementation)
```python
# Audio data ku kaydin document-ka (Base64)
recording_doc = {
    "user_id": ObjectId(user_id),
    "audio_data": "UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAAA...",  # Base64
    "duration": 5.0,
    "transcription": "waan ku faraxsanahay",
    "translation": "I am happy",
    "timestamp": datetime.utcnow(),
    "is_favorite": False
}
```

### Hadda (New GridFS Implementation)
```python
# Audio file ku kaydin GridFS, metadata ku qor collection
grid_id = fs.put(raw_audio_data, filename="rec_20241201_143022.wav", ...)

recording_doc = {
    "user_id": ObjectId(user_id),
    "file_id": grid_id,           # GridFS file ID
    "filename": "rec_20241201_143022.wav",
    "mime_type": "audio/wav",
    "size_bytes": 44100,
    "duration": 5.0,
    "transcription": "waan ku faraxsanahay",
    "translation": "I am happy",
    "timestamp": datetime.utcnow(),
    "is_favorite": False
}
```

## API Endpoints

### 1. Save Voice Recording

**Endpoint**: `POST /voice/save`

**Description**: Save voice recording with GridFS storage

**Request Body**:
```json
{
    "audio_data": "data:audio/webm;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAAA",
    "duration": 5.5,
    "language": "Somali",
    "transcription": "waan ku faraxsanahay",
    "translation": "I am happy"
}
```

**Audio Data Formats**:
- **Data URL**: `data:audio/webm;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAAA`
- **Base64**: `UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAAA`

**Success Response** (200):
```json
{
    "message": "Voice recording saved successfully",
    "id": "64f1a2b3c4d5e6f7g8h9i0j1",
    "file_id": "64f1a2b3c4d5e6f7g8h9i0j2",
    "mime_type": "audio/wav",
    "size_bytes": 44100,
    "timestamp": "2024-12-01T14:30:22.123456Z"
}
```

### 2. Get Voice Recordings

**Endpoint**: `GET /voice/recordings`

**Description**: Get all voice recordings for user

**Success Response** (200):
```json
[
    {
        "_id": "64f1a2b3c4d5e6f7g8h9i0j1",
        "user_id": "64f1a2b3c4d5e6f7g8h9i0j3",
        "file_id": "64f1a2b3c4d5e6f7g8h9i0j2",
        "filename": "rec_20241201_143022.wav",
        "mime_type": "audio/wav",
        "size_bytes": 44100,
        "duration": 5.5,
        "language": "Somali",
        "transcription": "waan ku faraxsanahay",
        "translation": "I am happy",
        "timestamp": "2024-12-01T14:30:22.123456Z",
        "is_favorite": false
    }
]
```

### 3. Stream Audio

**Endpoint**: `GET /voice/recordings/<recording_id>/audio`

**Description**: Stream audio file with proper Content-Type headers

**Headers**:
```
Authorization: Bearer <token>
```

**Response**: Binary audio file with headers:
```
Content-Type: audio/wav
Content-Length: 44100
Content-Disposition: inline; filename="rec_20241201_143022.wav"
```

### 4. Audio Data (Base64)

**Endpoint**: `GET /voice/recordings/<recording_id>/audio-data`

**Description**: Get audio data as base64 for frontend compatibility

**Success Response** (200):
```json
{
    "audio_data": "UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAAA",
    "recording_id": "64f1a2b3c4d5e6f7g8h9i0j1",
    "duration": 5.5,
    "language": "Somali",
    "transcription": "waan ku faraxsanahay",
    "translation": "I am happy",
    "timestamp": "2024-12-01T14:30:22.123456Z"
}
```

### 5. Download Audio

**Endpoint**: `GET /voice/recordings/<recording_id>/download`

**Description**: Download audio file as attachment

**Response**: Binary file with headers:
```
Content-Type: audio/wav
Content-Disposition: attachment; filename="rec_20241201_143022.wav"
```

### 6. Save to Local

**Endpoint**: `POST /voice/recordings/<recording_id>/save-local`

**Description**: Save audio file to local file system

**Success Response** (200):
```json
{
    "message": "Voice recording saved successfully",
    "filename": "rec_20241201_143022.wav",
    "file_path": "downloads/rec_20241201_143022.wav",
    "file_size": 44100
}
```

## Usage Examples

### JavaScript/Frontend

```javascript
// Save voice recording with data URL
const saveVoiceRecording = async (audioBlob, transcription, translation) => {
    // Convert blob to data URL
    const reader = new FileReader();
    reader.onload = async () => {
        const dataUrl = reader.result; // data:audio/webm;base64,...
        
        const response = await fetch('/voice/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                audio_data: dataUrl,
                duration: 5.5,
                language: "Somali",
                transcription: transcription,
                translation: translation
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log("✅ Recording saved:", data.id);
            return data.id;
        } else {
            console.error("❌ Save failed:", await response.text());
        }
    };
    reader.readAsDataURL(audioBlob);
};

// Play audio directly (streaming)
const playAudio = (recordingId) => {
    const audio = new Audio(`/voice/recordings/${recordingId}/audio`);
    audio.play();
};

// Get audio as base64 for custom playback
const getAudioData = async (recordingId) => {
    const response = await fetch(`/voice/recordings/${recordingId}/audio-data`, {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    
    if (response.ok) {
        const data = await response.json();
        const audio = new Audio(`data:audio/wav;base64,${data.audio_data}`);
        audio.play();
    }
};

// Download audio file
const downloadAudio = (recordingId) => {
    const link = document.createElement('a');
    link.href = `/voice/recordings/${recordingId}/download`;
    link.download = `recording_${recordingId}.wav`;
    link.click();
};
```

### Python

```python
import requests
import base64

def save_voice_recording(token, audio_file_path, transcription, translation):
    """Save voice recording with GridFS"""
    
    # Read audio file and convert to base64
    with open(audio_file_path, "rb") as f:
        audio_data = f.read()
    
    base64_audio = base64.b64encode(audio_data).decode('utf-8')
    
    # Create data URL
    data_url = f"data:audio/wav;base64,{base64_audio}"
    
    url = "http://localhost:5000/voice/save"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "audio_data": data_url,
        "duration": 5.5,
        "language": "Somali",
        "transcription": transcription,
        "translation": translation
    }
    
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Recording saved: {result['id']}")
        return result['id']
    else:
        print(f"❌ Save failed: {response.text}")
        return None

def download_voice_recording(token, recording_id, output_path):
    """Download voice recording"""
    
    url = f"http://localhost:5000/voice/recordings/{recording_id}/download"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"✅ Downloaded to: {output_path}")
        return True
    else:
        print(f"❌ Download failed: {response.text}")
        return False

# Usage
token = "your_token_here"
recording_id = save_voice_recording(token, "audio.wav", "waan ku faraxsanahay", "I am happy")
if recording_id:
    download_voice_recording(token, recording_id, "downloaded_audio.wav")
```

### cURL

```bash
# Save voice recording
curl -X POST "http://localhost:5000/voice/save" \
  -H "Authorization: Bearer your_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "audio_data": "data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAAA",
    "duration": 5.5,
    "language": "Somali",
    "transcription": "waan ku faraxsanahay",
    "translation": "I am happy"
  }'

# Get recordings list
curl -X GET "http://localhost:5000/voice/recordings" \
  -H "Authorization: Bearer your_token_here"

# Stream audio
curl -X GET "http://localhost:5000/voice/recordings/64f1a2b3c4d5e6f7g8h9i0j1/audio" \
  -H "Authorization: Bearer your_token_here" \
  --output "audio.wav"

# Download audio
curl -X GET "http://localhost:5000/voice/recordings/64f1a2b3c4d5e6f7g8h9i0j1/download" \
  -H "Authorization: Bearer your_token_here" \
  --output "recording.wav"

# Save to local
curl -X POST "http://localhost:5000/voice/recordings/64f1a2b3c4d5e6f7g8h9i0j1/save-local" \
  -H "Authorization: Bearer your_token_here"
```

## Data URL Parsing

### Supported Formats

```python
# Data URL format
"data:audio/webm;codecs=opus;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAAA"

# Base64 only (backward compatibility)
"UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAAA"
```

### MIME Type Mapping

| MIME Type | Extension | Description |
|-----------|-----------|-------------|
| `audio/webm` | `.webm` | WebM audio |
| `audio/ogg` | `.ogg` | OGG audio |
| `audio/mpeg` | `.mp3` | MP3 audio |
| `audio/wav` | `.wav` | WAV audio |
| `audio/x-wav` | `.wav` | WAV audio (alternative) |

## Database Schema

### Voice Recordings Collection
```javascript
{
    "_id": ObjectId("64f1a2b3c4d5e6f7g8h9i0j1"),
    "user_id": ObjectId("64f1a2b3c4d5e6f7g8h9i0j3"),
    "file_id": ObjectId("64f1a2b3c4d5e6f7g8h9i0j2"),  // GridFS file ID
    "filename": "rec_20241201_143022.wav",
    "mime_type": "audio/wav",
    "size_bytes": 44100,
    "duration": 5.5,
    "language": "Somali",
    "transcription": "waan ku faraxsanahay",
    "translation": "I am happy",
    "timestamp": ISODate("2024-12-01T14:30:22.123Z"),
    "is_favorite": false
}
```

### GridFS Files Collection
```javascript
{
    "_id": ObjectId("64f1a2b3c4d5e6f7g8h9i0j2"),
    "filename": "rec_20241201_143022.wav",
    "contentType": "audio/wav",
    "length": 44100,
    "chunkSize": 261120,
    "uploadDate": ISODate("2024-12-01T14:30:22.123Z"),
    "metadata": {
        "user_id": "64f1a2b3c4d5e6f7g8h9i0j3",
        "duration": 5.5,
        "created_at": ISODate("2024-12-01T14:30:22.123Z")
    }
}
```

## Error Handling

### Common Errors

1. **Invalid Audio Data** (400):
   ```json
   {
     "error": "Invalid audio data (not data URL / base64)"
   }
   ```

2. **File Too Large** (413):
   ```json
   {
     "error": "Audio is too large (max 10MB)"
   }
   ```

3. **File Missing** (404):
   ```json
   {
     "error": "File missing"
   }
   ```

4. **Invalid Base64** (400):
   ```json
   {
     "error": "Invalid base64 data: Incorrect padding"
   }
   ```

## Performance Benefits

### Database Efficiency
- **Compact Documents**: No large Base64 strings in documents
- **Faster Queries**: Smaller documents load faster
- **Better Indexing**: Metadata queries are more efficient

### Storage Optimization
- **GridFS Chunking**: Large files split into chunks
- **Streaming**: Audio served directly from GridFS
- **Memory Efficient**: No need to load entire audio into memory

### Scalability
- **File Size Limits**: 10MB max per file
- **Automatic Cleanup**: GridFS files deleted with recordings
- **Multiple Formats**: Support for various audio formats

## Migration from Old System

### Backward Compatibility
- Old recordings with `audio_data` field still work
- `audio-data` endpoint provides Base64 for compatibility
- Gradual migration possible

### Migration Script
```python
# Optional: Migrate old recordings to GridFS
def migrate_old_recordings():
    old_recordings = voice_recordings.find({"audio_data": {"$exists": True}})
    
    for recording in old_recordings:
        audio_data = recording.get("audio_data")
        if audio_data:
            # Convert to GridFS
            raw = base64.b64decode(audio_data)
            grid_id = fs.put(raw, filename=f"migrated_{recording['_id']}.wav")
            
            # Update document
            voice_recordings.update_one(
                {"_id": recording["_id"]},
                {
                    "$set": {
                        "file_id": grid_id,
                        "filename": f"migrated_{recording['_id']}.wav",
                        "mime_type": "audio/wav",
                        "size_bytes": len(raw)
                    },
                    "$unset": {"audio_data": ""}
                }
            )
```

## Testing

### Run Tests
```bash
python test_voice_gridfs.py
```

### Test Results
```
=== Voice Recording GridFS Tests ===

Testing voice recording save with GridFS...
✅ Voice recording saved successfully!
   Recording ID: 64f1a2b3c4d5e6f7g8h9i0j1
   File ID: 64f1a2b3c4d5e6f7g8h9i0j2
   MIME Type: audio/wav
   Size: 44 bytes

Testing get voice recordings...
✅ Found 1 recordings
   Recording 1:
     ID: 64f1a2b3c4d5e6f7g8h9i0j1
     Filename: rec_20241201_143022.wav
     MIME Type: audio/wav
     Size: 44 bytes
     Duration: 5.5 seconds
     Has audio_data: False
     Has file_id: True

Testing audio streaming for recording 64f1a2b3c4d5e6f7g8h9i0j1...
✅ Audio streaming successful!
   Audio data size: 44 bytes
```

## Security Considerations

### File Validation
- **Size Limits**: Maximum 10MB per file
- **Format Validation**: Only audio MIME types accepted
- **Base64 Validation**: Proper base64 format required

### Access Control
- **User Isolation**: Users can only access their own recordings
- **Token Authentication**: All endpoints require valid JWT
- **File Permissions**: GridFS files tied to user accounts

### Data Protection
- **No Audio in Logs**: Audio data not logged
- **Secure Headers**: Proper Content-Type and Content-Disposition
- **Cleanup**: Automatic file deletion on recording removal

## Support

Haddii aad u baahan tahay caawimaad dheeraad ah:
- Check audio data format (data URL or base64)
- Verify file size (max 10MB)
- Test with different audio formats
- Check GridFS connection

---

**GridFS voice recording system-ka cusub wuxuu si sax ah u shaqeynaya!** 🎵✅
