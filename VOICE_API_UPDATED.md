# Voice API - Updated with Language Detection

## Overview

Voice API-ga cusub wuxuu ka saaray speech-to-text iyo translation backend-ka. Hadda frontend-ka ayaa sameynaya speech-to-text iyo translation, backend-ka kalena wuxuu:
1. **Hubinaya** luqadda transcription-ka
2. **Keydinaya** codka iyo qoraalka database-ka
3. **Soo celinaya** codka playback-ka

## API Endpoints

### POST `/voice/save`

**Description**: Keydi codka iyo qoraalka user-ka

**Headers**:
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "audio_data": "base64_encoded_audio_data",
  "duration": 5,
  "language": "Somali",
  "transcription": "waan ku faraxsanahay",
  "translation": "I am happy"
}
```

**Required Fields**:
- `audio_data`: Base64 encoded audio data
- `transcription`: Qoraalka codka (waa la baahanahay)

**Optional Fields**:
- `duration`: Duration-ka codka (seconds)
- `language`: Luqadda (default: "Somali")
- `translation`: Turjumaada qoraalka

**Language Detection**:
- Backend-ku wuxuu hubinaya transcription-ka luqaddiisa
- Haddii luqaddu **aan Somali ahayn** → error: `"Fadlan ku hadal Somali"`
- Haddii Somali tahay → keydi database-ka

**Success Response** (200):
```json
{
  "message": "Voice recording saved successfully",
  "id": "recording_id",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

**Error Responses**:
- `400`: "Audio data is required"
- `400`: "Transcription is required"
- `400`: "Fadlan ku hadal Somali"
- `403`: "Invalid token payload"
- `500`: Server error

### GET `/voice/recordings`

**Description**: Soo qaad dhammaan codka user-ka

**Headers**:
```
Authorization: Bearer <token>
```

**Success Response** (200):
```json
[
  {
    "_id": "recording_id",
    "user_id": "user_id",
    "audio_data": "base64_encoded_audio",
    "duration": 5,
    "language": "Somali",
    "transcription": "waan ku faraxsanahay",
    "translation": "I am happy",
    "timestamp": "2024-01-01T12:00:00.000Z",
    "is_favorite": false
  }
]
```

### GET `/voice/recordings/<recording_id>`

**Description**: Soo qaad codka gaarka ah

**Headers**:
```
Authorization: Bearer <token>
```

**Success Response** (200):
```json
{
  "_id": "recording_id",
  "user_id": "user_id",
  "audio_data": "base64_encoded_audio",
  "duration": 5,
  "language": "Somali",
  "transcription": "waan ku faraxsanahay",
  "translation": "I am happy",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "is_favorite": false
}
```

### GET `/voice/recordings/<recording_id>/audio-data`

**Description**: Soo qaad codka iyo xogtiisa playback-ka

**Headers**:
```
Authorization: Bearer <token>
```

**Success Response** (200):
```json
{
  "audio_data": "base64_encoded_audio",
  "recording_id": "recording_id",
  "duration": 5,
  "language": "Somali",
  "transcription": "waan ku faraxsanahay",
  "translation": "I am happy",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### GET `/voice/recordings/<recording_id>/audio`

**Description**: Soo qaad codka audio file ahaan

**Headers**:
```
Authorization: Bearer <token>
```

**Success Response** (200):
- Audio file with headers:
  - `Content-Type: audio/wav`
  - `Content-Disposition: attachment; filename=recording_<id>.wav`

## Frontend Integration

### Workflow

1. **Duub codka** (frontend)
2. **Speech-to-text** (frontend)
3. **Translate** (frontend)
4. **Send to backend**:
   ```javascript
   const response = await fetch('/voice/save', {
     method: 'POST',
     headers: {
       'Authorization': `Bearer ${token}`,
       'Content-Type': 'application/json'
     },
     body: JSON.stringify({
       audio_data: base64Audio,
       duration: audioDuration,
       language: 'Somali',
       transcription: somaliText,
       translation: englishText
     })
   });
   ```

### Error Handling

```javascript
if (response.status === 400) {
  const error = await response.json();
  if (error.error === "Fadlan ku hadal Somali") {
    // Show message to user to speak Somali
    showMessage("Fadlan ku hadal Somali");
  } else if (error.error === "Transcription is required") {
    // Show message that transcription is needed
    showMessage("Waxaa loo baahan yahay qoraalka codka");
  }
}
```

### Playback

```javascript
// Get audio data for playback
const audioResponse = await fetch(`/voice/recordings/${recordingId}/audio-data`, {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const audioData = await audioResponse.json();
const audioBlob = base64ToBlob(audioData.audio_data, 'audio/wav');
const audioUrl = URL.createObjectURL(audioBlob);

// Play audio
const audio = new Audio(audioUrl);
audio.play();
```

## Testing

Isticmaal `test_voice_api_updated.py` si aad u test-gareysato API-ga:

```bash
python test_voice_api_updated.py
```

**Test Cases**:
1. ✅ Save with Somali transcription
2. ✅ Reject English transcription
3. ✅ Reject missing transcription
4. ✅ Get audio data for playback

## Database Schema

```javascript
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "audio_data": String,        // Base64 encoded
  "duration": Number,          // Seconds
  "language": String,          // "Somali"
  "transcription": String,     // Somali text
  "translation": String,       // English text
  "timestamp": Date,
  "is_favorite": Boolean
}
```

## Dependencies

- `langdetect`: Language detection
- `pymongo`: MongoDB connection
- `flask`: Web framework
- `PyJWT`: JWT authentication
