# Voice API - Base64 Audio Handling Guide

## Overview

Voice API-ga cusub wuxuu leeyahay **Base64 audio handling** oo buuxa. Waxaad ka soo qaadi kartaa codadka siday u kala duwan yihiin:

1. **Download WAV file** - Direct download
2. **Save to server** - Save locally on server
3. **Base64 data** - For frontend playback

## API Endpoints

### 1. Download Voice Recording

**Endpoint**: `GET /voice/recordings/{recording_id}/download`

**Description**: Soo qaad codka sidii WAV file download ah

**Headers**:
```
Authorization: Bearer <token>
```

**Response**: WAV file with headers:
- `Content-Type: audio/wav`
- `Content-Disposition: attachment; filename="recording_{id}_{timestamp}.wav"`

**Example**:
```bash
curl -X GET "http://localhost:5000/voice/recordings/64f1a2b3c4d5e6f7g8h9i0j1/download" \
  -H "Authorization: Bearer your_token_here" \
  --output "my_recording.wav"
```

### 2. Save Voice Recording Locally

**Endpoint**: `POST /voice/recordings/{recording_id}/save-local`

**Description**: Keydi codka server-ka local filesystem-ka

**Headers**:
```
Authorization: Bearer <token>
```

**Response** (200):
```json
{
  "message": "Voice recording saved successfully",
  "filename": "recording_64f1a2b3c4d5e6f7g8h9i0j1_20241201_143022.wav",
  "file_path": "downloads/recording_64f1a2b3c4d5e6f7g8h9i0j1_20241201_143022.wav",
  "file_size": 12345
}
```

**Example**:
```bash
curl -X POST "http://localhost:5000/voice/recordings/64f1a2b3c4d5e6f7g8h9i0j1/save-local" \
  -H "Authorization: Bearer your_token_here"
```

### 3. Get Base64 Audio Data

**Endpoint**: `GET /voice/recordings/{recording_id}/audio-data`

**Description**: Soo qaad codka Base64 format ah frontend playback-ka

**Headers**:
```
Authorization: Bearer <token>
```

**Response** (200):
```json
{
  "audio_data": "UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAABCxAgAEABAAZGF0YQAAAAAA...",
  "recording_id": "64f1a2b3c4d5e6f7g8h9i0j1",
  "duration": 5,
  "language": "Somali",
  "transcription": "waan ku faraxsanahay",
  "translation": "I am happy",
  "timestamp": "2024-12-01T14:30:22.000Z"
}
```

## Base64 Audio Handling

### Backend Processing

```python
import base64

def process_base64_audio(audio_data_b64):
    """Process Base64 audio data"""
    try:
        # Decode Base64 to binary
        audio_bytes = base64.b64decode(audio_data_b64)
        
        # Save as WAV file
        with open("output.wav", "wb") as f:
            f.write(audio_bytes)
        
        print("Codka waa la kaydiyey, hadda waad ciyaarsan kartaa")
        return True
        
    except Exception as e:
        print(f"Khalad: {str(e)}")
        return False
```

### Frontend Playback

```javascript
// Get Base64 audio data
const response = await fetch(`/voice/recordings/${recordingId}/audio-data`, {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const data = await response.json();

// Convert Base64 to Blob
const base64Data = data.audio_data;
const byteCharacters = atob(base64Data);
const byteNumbers = new Array(byteCharacters.length);

for (let i = 0; i < byteCharacters.length; i++) {
  byteNumbers[i] = byteCharacters.charCodeAt(i);
}

const byteArray = new Uint8Array(byteNumbers);
const blob = new Blob([byteArray], { type: 'audio/wav' });

// Create and play audio
const audio = new Audio(URL.createObjectURL(blob));
await audio.play();
```

## Usage Examples

### Python Example

```python
import requests
import base64

def download_and_play_audio(recording_id, token):
    """Download and play voice recording"""
    
    # Download audio file
    response = requests.get(
        f"http://localhost:5000/voice/recordings/{recording_id}/download",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        # Save to local file
        filename = f"recording_{recording_id}.wav"
        with open(filename, "wb") as f:
            f.write(response.content)
        
        print(f"Codka waa la kaydiyey: {filename}")
        return filename
    else:
        print("Khalad markii la soo qaadinayay codka")
        return None

def save_and_play(audio_data_b64):
    """Save Base64 audio and play"""
    # Decode Base64
    audio_bytes = base64.b64decode(audio_data_b64)
    
    # Save file locally
    with open("output.wav", "wb") as f:
        f.write(audio_bytes)
    
    print("Codka waa la kaydiyey, hadda waad ciyaarsan kartaa")
```

### JavaScript Example

```javascript
// Download audio file
async function downloadAudio(recordingId, token) {
  const response = await fetch(`/voice/recordings/${recordingId}/download`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  if (response.ok) {
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    
    // Create download link
    const a = document.createElement('a');
    a.href = url;
    a.download = `recording_${recordingId}.wav`;
    a.click();
    
    URL.revokeObjectURL(url);
  }
}

// Play Base64 audio
async function playBase64Audio(recordingId, token) {
  const response = await fetch(`/voice/recordings/${recordingId}/audio-data`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  const data = await response.json();
  
  // Convert Base64 to audio
  const audio = new Audio(`data:audio/wav;base64,${data.audio_data}`);
  await audio.play();
}
```

### Flutter Example

```dart
import 'dart:convert';
import 'dart:io';
import 'package:path_provider/path_provider.dart';
import 'package:audioplayers/audioplayers.dart';

Future<void> playBase64Audio(String base64Audio) async {
  // Decode Base64
  final audioBytes = base64Decode(base64Audio);

  // Save file temp
  final dir = await getTemporaryDirectory();
  final file = File('${dir.path}/playback.wav');
  await file.writeAsBytes(audioBytes);

  // Play
  final player = AudioPlayer();
  await player.play(DeviceFileSource(file.path));
}

// Usage with API
Future<void> playRecording(String recordingId, String token) async {
  final response = await http.get(
    Uri.parse('http://localhost:5000/voice/recordings/$recordingId/audio-data'),
    headers: {'Authorization': 'Bearer $token'},
  );
  
  if (response.statusCode == 200) {
    final data = jsonDecode(response.body);
    await playBase64Audio(data['audio_data']);
  }
}
```

## File Structure

### Downloads Directory
```
project_api/
├── downloads/
│   ├── recording_64f1a2b3c4d5e6f7g8h9i0j1_20241201_143022.wav
│   ├── recording_64f1a2b3c4d5e6f7g8h9i0j2_20241201_143045.wav
│   └── ...
```

### Filename Format
- `recording_{id}_{timestamp}.wav`
- Example: `recording_64f1a2b3c4d5e6f7g8h9i0j1_20241201_143022.wav`

## Error Handling

### Common Errors

1. **Invalid Base64**:
   ```json
   {
     "error": "Invalid audio data format: Incorrect padding"
   }
   ```

2. **Recording not found**:
   ```json
   {
     "error": "Recording not found"
   }
   ```

3. **Audio data not found**:
   ```json
   {
     "error": "Audio data not found"
   }
   ```

### Error Handling Example

```javascript
try {
  const response = await fetch(`/voice/recordings/${recordingId}/download`);
  
  if (!response.ok) {
    const error = await response.json();
    console.error('Error:', error.error);
    return;
  }
  
  // Process successful response
  const blob = await response.blob();
  // ... handle audio
  
} catch (error) {
  console.error('Network error:', error);
}
```

## Testing

### Run Tests
```bash
python test_voice_base64_handling.py
```

### Test Cases
1. ✅ Download voice recording as WAV file
2. ✅ Save voice recording to local server
3. ✅ Get Base64 audio data for playback
4. ✅ Base64 to WAV conversion

## Security Considerations

### Authentication
- All endpoints require valid JWT token
- User can only access their own recordings

### File Security
- Files saved to `downloads/` directory
- Automatic cleanup of test files
- Proper file permissions

### Input Validation
- Base64 validation before processing
- File size limits
- Audio format validation

## Performance Tips

### Frontend Optimization
- Use `URL.createObjectURL()` for efficient blob handling
- Clean up blob URLs after use
- Implement audio caching for repeated playback

### Backend Optimization
- Stream large files instead of loading into memory
- Implement file compression for storage
- Use CDN for static file serving

## Troubleshooting

### Audio Not Playing
1. Check if Base64 data is valid
2. Verify audio format (WAV)
3. Check browser console for errors
4. Ensure proper MIME type

### Download Issues
1. Verify authentication token
2. Check file permissions
3. Ensure sufficient disk space
4. Check network connectivity

### Base64 Decoding Errors
1. Validate Base64 string format
2. Check for padding issues
3. Verify encoding/decoding process
4. Test with known good data

## API Reference Summary

| Endpoint | Method | Description | Response |
|----------|--------|-------------|----------|
| `/voice/recordings/{id}/download` | GET | Download WAV file | Audio file |
| `/voice/recordings/{id}/save-local` | POST | Save to server | JSON |
| `/voice/recordings/{id}/audio-data` | GET | Get Base64 data | JSON |

## Support

Haddii aad u baahan tahay caawimaad dheeraad ah:
- Check error messages carefully
- Verify API documentation
- Test with provided examples
- Contact development team
