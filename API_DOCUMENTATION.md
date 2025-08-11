# Somali Translator API Documentation

## Base URL
```
http://localhost:5000
```

## Authentication
Most endpoints require authentication using JWT tokens. Include the token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## API Endpoints

### Health Check
Check if the API is running and healthy.

#### GET /health
**Description**: Health check endpoint to verify backend status

**Response**:
```json
{
  "status": "healthy",
  "message": "Somali Translator API is running",
  "timestamp": "2024-01-01T12:00:00.000000",
  "version": "1.0.0"
}
```

#### GET /api/health
**Description**: Alternative health check endpoint with /api prefix

**Response**: Same as `/health`

### Authentication
- `POST /register` - Register a new user
- `POST /login` - Login user
- `POST /logout` - Logout user

### Translation
- `POST /translate` - Translate text (works with or without authentication)
- `GET /history` - Get all translations (public)

### History (Authenticated)
- `GET /history` - Get user's translation history with pagination
- `GET /history/<translation_id>` - Get specific translation from history
- `DELETE /history/<translation_id>` - Delete specific translation from history
- `DELETE /history` - Clear all user's translation history

### Favorites
- `POST /favorite` - Add translation to favorites (authenticated)
- `GET /favorites` - Get all favorites (public)
- `GET /user/favorites` - Get user's favorites (authenticated)
- `DELETE /favorites/<fav_id>` - Delete specific favorite
- `DELETE /favorites` - Clear all favorites

### User Management
- `GET /users` - Get all users (public)
- `GET /users/<user_id>` - Get specific user
- `PUT /users/<user_id>` - Update user
- `DELETE /users/<user_id>` - Delete user
- `GET /users/count` - Get total user count
- `GET /user/stats` - Get user statistics (authenticated)

### Language Detection
- `POST /detect-language` - Detect if text is Somali or other language
- `POST /is-somali` - Simple check if text is Somali
- `POST /analyze-text` - Detailed analysis of text for Somali characteristics

### Voice Translation
- `POST /voice/translate` - Upload audio file with transcribed text and get translation
- `GET /voice/history` - Get user's voice translation history
- `GET /voice/<voice_id>` - Get specific voice translation
- `DELETE /voice/<voice_id>` - Delete specific voice translation
- `DELETE /voice` - Clear all voice history
- `GET /voice/<voice_id>/audio` - Download audio file

### Admin Dashboard (Admin Only)
- `GET /admin/dashboard` - Get dashboard statistics
- `GET /admin/users` - Get all users with pagination
- `POST /admin/users/<user_id>/suspend` - Suspend user
- `POST /admin/users/<user_id>/unsuspend` - Unsuspend user
- `GET /admin/users/<user_id>/stats` - Get detailed user statistics

### Analytics & Reports (Admin Only)
- `GET /admin/analytics` - Get comprehensive analytics
- `GET /admin/reports/export` - Export reports data

## Detailed Endpoint Documentation

### Authentication Endpoints

#### Register User
```http
POST /register
Content-Type: application/json

{
  "full_name": "John Doe",
  "email": "john@example.com",
  "password": "password123"
}
```

#### Login User
```http
POST /login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "password123"
}
```

### Translation Endpoints

#### Translate Text
```http
POST /translate
Content-Type: application/json
Authorization: Bearer <token> (optional)

{
  "text": "Hello, how are you?"
}
```

Response:
```json
{
  "translated_text": "Halkan, sidee tahay?",
  "id": "507f1f77bcf86cd799439011"
}
```

#### Get User History
```http
GET /history?page=1&limit=20
Authorization: Bearer <token>
```

#### Get Specific Translation from History
```http
GET /history/<translation_id>
Authorization: Bearer <token>
```

#### Delete Translation from History
```http
DELETE /history/<translation_id>
Authorization: Bearer <token>
```

#### Clear All History
```http
DELETE /history
Authorization: Bearer <token>
```

#### Get User Favorites
```http
GET /user/favorites?page=1&limit=20
Authorization: Bearer <token>
```

### Admin Dashboard Endpoints

#### Get Dashboard Statistics
```http
GET /admin/dashboard
Authorization: Bearer <admin_token>
```

Response:
```json
{
  "total_users": 150,
  "active_users_today": 45,
  "suspended_users": 3,
  "translations_today": 2847,
  "translations_week": 18234,
  "translations_month": 76589,
  "total_favorites": 1234,
  "top_users_month": [
    {
      "user_id": "507f1f77bcf86cd799439011",
      "full_name": "John Doe",
      "email": "john@example.com",
      "translation_count": 156
    }
  ],
  "top_users_week": [...]
}
```

#### Get All Users (Admin)
```http
GET /admin/users?page=1&limit=10
Authorization: Bearer <admin_token>
```

Response:
```json
{
  "users": [
    {
      "_id": "507f1f77bcf86cd799439011",
      "full_name": "John Doe",
      "email": "john@example.com",
      "role": "user",
      "is_suspended": false,
      "created_at": "2024-01-01T00:00:00Z",
      "last_login": "2024-01-15T10:30:00Z",
      "translations_count": 156,
      "favorites_count": 23
    }
  ],
  "total": 150,
  "page": 1,
  "limit": 10,
  "pages": 15
}
```

#### Suspend/Unsuspend User
```http
POST /admin/users/<user_id>/suspend
Authorization: Bearer <admin_token>

POST /admin/users/<user_id>/unsuspend
Authorization: Bearer <admin_token>
```

### Language Detection Endpoints

#### Detect Language
```http
POST /detect-language
Content-Type: application/json

{
  "text": "Waxaan ku jiraa halkan"
}
```

Response:
```json
{
  "text": "Waxaan ku jiraa halkan",
  "language_detection": {
    "detected_language": "so",
    "language_confidence": 0.85,
    "detection_method": "pattern_matching",
    "is_somali": true,
    "language_name": "Somali"
  }
}
```

#### Check if Somali
```http
POST /is-somali
Content-Type: application/json

{
  "text": "Hello, how are you?",
  "confidence_threshold": 0.5
}
```

Response:
```json
{
  "text": "Hello, how are you?",
  "is_somali": false,
  "confidence_threshold": 0.5
}
```

#### Analyze Text
```http
POST /analyze-text
Content-Type: application/json

{
  "text": "Salaan, sidee tahay maanta?"
}
```

Response:
```json
{
  "text": "Salaan, sidee tahay maanta?",
  "analysis": {
    "detected_language": "so",
    "confidence": 0.9,
    "method": "pattern_matching",
    "is_somali": true,
    "total_words": 4,
    "somali_words_count": 3,
    "somali_words_found": ["salaan", "sidee", "maanta"],
    "somali_characteristics_score": 0.75,
    "somali_ratio": 0.75
  }
}
```

### Voice Translation Endpoints

#### Upload Audio with Text and Translate
```http
POST /voice/translate
Content-Type: multipart/form-data
Authorization: Bearer <token>

Form Data:
- audio: <recorded_audio_file> (wav, mp3, m4a, flac, ogg, webm) - Audio recorded from frontend microphone
- transcribed_text: "Transcribed text from frontend speech recognition"
```

Response:
```json
{
  "message": "Voice recording and translation saved successfully",
  "voice_translation_id": "507f1f77bcf86cd799439011",
  "transcribed_text": "Salaan, sidee tahay?",
  "translated_text": "Hello, how are you?",
  "audio_filename": "20231201_143022_audio.wav",
  "language_detection": {
    "detected_language": "so",
    "language_confidence": 0.85,
    "detection_method": "pattern_matching",
    "is_somali": true
  }
}
```

#### Get Voice History
```http
GET /voice/history?page=1&limit=20
Authorization: Bearer <token>
```

Response:
```json
{
  "voice_translations": [
    {
      "_id": "507f1f77bcf86cd799439011",
      "user_id": "507f1f77bcf86cd799439012",
      "audio_filename": "20231201_143022_audio.wav",
      "transcribed_text": "Salaan, sidee tahay?",
      "translated_text": "Hello, how are you?",
      "timestamp": "2023-12-01T14:30:22+03:00",
      "is_favorite": false,
      "detected_language": "so",
      "language_confidence": 0.85,
      "detection_method": "pattern_matching"
    }
  ],
  "total": 25,
  "page": 1,
  "limit": 20,
  "pages": 2
}
```

#### Get Specific Voice Translation
```http
GET /voice/<voice_id>
Authorization: Bearer <token>
```

#### Delete Voice Translation
```http
DELETE /voice/<voice_id>
Authorization: Bearer <token>
```

#### Clear All Voice History
```http
DELETE /voice
Authorization: Bearer <token>
```

#### Download Audio File
```http
GET /voice/<voice_id>/audio
Authorization: Bearer <token>
```

### Analytics Endpoints

#### Get Analytics
```http
GET /admin/analytics
Authorization: Bearer <admin_token>
```

Response:
```json
{
  "translation_volume": {
    "today": 2847,
    "this_week": 18234,
    "this_month": 76589
  },
  "user_engagement": {
    "daily_active_users": 45,
    "weekly_active_users": 89,
    "monthly_active_users": 134
  },
  "popular_features": {
    "favorites_used": 1234,
    "history_accessed": 5678,
    "voice_input_used": 0
  },
  "usage_patterns": [
    {
      "date": "2024-01-15",
      "count": 2847
    }
  ],
  "user_retention": [
    {
      "week": "2024-01-08",
      "active_users": 89
    }
  ]
}
```

## Error Responses

All endpoints return consistent error responses:

```json
{
  "error": "Error message description"
}
```

### Language Detection Errors

When non-Somali text is detected, the translation endpoints return a 400 error:

```json
{
  "error": "Qoraalka aad galiyay ma aha afka Soomaaliga. Fadlan gali qoraal Soomaali ah.",
  "language_detection": {
    "detected_language": "other",
    "language_confidence": 0.8,
    "detection_method": "combined_analysis",
    "is_somali": false
  }
}
```

**Translation:** "The text you entered is not Somali language. Please enter Somali text."

Common HTTP status codes:
- `200` - Success
- `400` - Bad Request (including language detection errors)
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

## Data Models

### User
```json
{
  "_id": "ObjectId",
  "full_name": "string",
  "email": "string",
  "password": "string (hashed)",
  "role": "user|admin",
  "is_suspended": "boolean",
  "created_at": "datetime",
  "last_login": "datetime"
}
```

### Translation
```json
{
  "_id": "ObjectId",
  "original_text": "string",
  "translated_text": "string",
  "user_id": "ObjectId (optional)",
  "timestamp": "datetime",
  "is_favorite": "boolean",
  "detected_language": "so|other",
  "language_confidence": "float",
  "detection_method": "string"
}
```

### Favorite
```json
{
  "_id": "ObjectId",
  "user_id": "ObjectId",
  "original_text": "string",
  "translated_text": "string",
  "translation_id": "ObjectId (optional)",
  "timestamp": "datetime",
  "is_favorite": "boolean"
}
```

### Voice Translation
```json
{
  "_id": "ObjectId",
  "user_id": "ObjectId",
  "audio_filename": "string",
  "audio_path": "string",
  "original_text": "string",
  "translated_text": "string",
  "timestamp": "datetime",
  "is_favorite": "boolean",
  "detected_language": "so|other",
  "language_confidence": "float",
  "detection_method": "string"
}
```

## Notes

1. All timestamps are in Somalia timezone (Africa/Mogadishu)
2. User authentication is required for most endpoints
3. Admin endpoints require admin role
4. Pagination is available for list endpoints
5. The translation endpoint works for both authenticated and anonymous users
