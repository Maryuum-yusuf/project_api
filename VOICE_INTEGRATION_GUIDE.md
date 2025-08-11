# Voice Recorder Integration Guide

## Quick Start

### 1. Include the Voice Recorder Script
```html
<script src="/static/js/voice-recorder.js"></script>
```

### 2. Add a Container Element
```html
<div id="voiceRecorder"></div>
```

### 3. Initialize the Voice Recorder
```javascript
const voiceRecorder = new VoiceRecorder('voiceRecorder', {
    maxRecordingTime: 60000, // 60 seconds
    sampleRate: 44100
});
```

## Complete Integration Example

```html
<!DOCTYPE html>
<html>
<head>
    <title>My App with Voice Recorder</title>
</head>
<body>
    <h1>My Application</h1>
    
    <!-- Voice Recorder Container -->
    <div id="voiceRecorder"></div>
    
    <!-- Include the voice recorder script -->
    <script src="/static/js/voice-recorder.js"></script>
    
    <script>
        // Initialize voice recorder
        const voiceRecorder = new VoiceRecorder('voiceRecorder', {
            maxRecordingTime: 60000,
            sampleRate: 44100
        });
        
        // Make sure user is authenticated
        const token = localStorage.getItem('authToken');
        if (!token) {
            console.log('User needs to be logged in to use voice recorder');
        }
    </script>
</body>
</html>
```

## Configuration Options

```javascript
const voiceRecorder = new VoiceRecorder('containerId', {
    maxRecordingTime: 60000,    // Maximum recording time in milliseconds
    sampleRate: 44100,          // Audio sample rate
    audioFormat: 'webm'         // Audio format (webm is recommended for browser)
});
```

## Authentication

The voice recorder requires authentication. Make sure the user is logged in and the token is stored:

```javascript
// After successful login
localStorage.setItem('authToken', userToken);

// Or use sessionStorage
sessionStorage.setItem('authToken', userToken);
```

## API Endpoints Used

The voice recorder automatically uses these endpoints:

- `POST /voice/translate` - Upload and translate audio
- `GET /voice/history` - Get voice translation history
- `DELETE /voice/<voice_id>` - Delete voice translation

## Customization

### Custom Styling
The voice recorder includes its own CSS, but you can override it:

```css
.voice-recorder {
    /* Your custom styles */
}

.record-btn {
    /* Custom button styles */
}
```

### Event Handling
You can listen for recording events:

```javascript
// Listen for recording start
document.addEventListener('recordingStarted', function() {
    console.log('Recording started');
});

// Listen for recording stop
document.addEventListener('recordingStopped', function() {
    console.log('Recording stopped');
});

// Listen for translation success
document.addEventListener('translationSuccess', function(event) {
    console.log('Translation result:', event.detail);
});
```

## Browser Compatibility

The voice recorder uses the MediaRecorder API, which is supported in:

- Chrome 47+
- Firefox 25+
- Safari 14.1+
- Edge 79+

## Error Handling

The voice recorder handles common errors:

- Microphone permission denied
- Network errors
- Authentication errors
- File upload errors

Error messages are displayed to the user automatically.

## Demo Page

Visit `/voice-demo` to see a complete working example of the voice recorder.

## Troubleshooting

### Microphone Not Working
1. Check browser permissions
2. Ensure HTTPS is used (required for microphone access)
3. Check if microphone is connected and working

### Authentication Errors
1. Make sure user is logged in
2. Check if token is stored in localStorage/sessionStorage
3. Verify token is valid and not expired

### Upload Errors
1. Check file size limits
2. Ensure audio format is supported
3. Verify network connection

## Advanced Usage

### Custom Success Handler
```javascript
// Override the default success handler
voiceRecorder.showSuccess = function(result) {
    // Custom success handling
    console.log('Custom success:', result);
    
    // You can integrate with your app's UI
    displayTranslation(result.original_text, result.translated_text);
};
```

### Custom Error Handler
```javascript
// Override the default error handler
voiceRecorder.showError = function(message) {
    // Custom error handling
    console.error('Custom error:', message);
    
    // You can integrate with your app's error system
    showNotification(message, 'error');
};
```

## Security Considerations

1. **HTTPS Required**: Microphone access requires HTTPS in production
2. **User Consent**: Always get user permission before accessing microphone
3. **Token Security**: Store authentication tokens securely
4. **File Validation**: The API validates file types and sizes
5. **User Isolation**: Users can only access their own recordings

## Performance Tips

1. **Limit Recording Time**: Set reasonable maxRecordingTime
2. **Audio Quality**: Use appropriate sample rate (44100 is good quality)
3. **File Size**: Keep recordings under 10MB for better performance
4. **Cleanup**: The recorder automatically cleans up audio URLs

## Integration with React/Vue/Angular

### React Example
```jsx
import React, { useEffect, useRef } from 'react';

function VoiceRecorderComponent() {
    const containerRef = useRef(null);
    const voiceRecorderRef = useRef(null);
    
    useEffect(() => {
        if (containerRef.current && !voiceRecorderRef.current) {
            voiceRecorderRef.current = new VoiceRecorder(containerRef.current.id, {
                maxRecordingTime: 60000
            });
        }
        
        return () => {
            // Cleanup if needed
        };
    }, []);
    
    return <div id="voiceRecorder" ref={containerRef} />;
}
```

### Vue Example
```vue
<template>
    <div id="voiceRecorder" ref="voiceRecorderContainer"></div>
</template>

<script>
export default {
    mounted() {
        this.voiceRecorder = new VoiceRecorder('voiceRecorder', {
            maxRecordingTime: 60000
        });
    },
    
    beforeDestroy() {
        // Cleanup if needed
    }
}
</script>
```

This integration guide provides everything you need to add voice recording functionality to your application!
