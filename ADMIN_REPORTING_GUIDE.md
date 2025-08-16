# Admin Reporting System Guide

## Overview

Admin reporting system-ka cusub wuxuu leeyahay **comprehensive reporting capabilities** oo leh **date filtering** oo buuxa. Waxaad ka soo qaadi kartaa translations-ka iyo statistics-ka siday u kala duwan yihiin:

1. **Date Filtering**: Year, month, custom date range
2. **Detailed Reports**: Translations with user details
3. **Summary Statistics**: Monthly and yearly overview
4. **Export Functionality**: CSV format
5. **Analytics**: User engagement and usage patterns

## API Endpoints

### 1. Translations Report

**Endpoint**: `GET /admin/reports/translations`

**Description**: Soo qaad detailed translations report with filtering

**Query Parameters**:
- `year`: Specific year (e.g., 2024)
- `month`: Specific month (1-12)
- `start_date`: Custom start date (YYYY-MM-DD)
- `end_date`: Custom end date (YYYY-MM-DD)
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 50)

**Headers**:
```
Authorization: Bearer <admin_token>
```

**Response** (200):
```json
{
    "translations": [
        {
            "_id": "64f1a2b3c4d5e6f7g8h9i0j1",
            "user_name": "Ahmed Hassan",
            "user_email": "ahmed@example.com",
            "timestamp": "2024-12-01T10:30:00Z",
            "original_text": "Hello world",
            "translated_text": "Salaam dunida",
            "source_language": "English",
            "target_language": "Somali"
        }
    ],
    "total": 150,
    "page": 1,
    "limit": 50,
    "pages": 3,
    "statistics": {
        "total_translations": 150,
        "unique_users": 25,
        "language_pairs": [
            {
                "_id": {
                    "source": "English",
                    "target": "Somali"
                },
                "count": 120
            }
        ]
    },
    "date_filter": {
        "start_date": "2024-12-01",
        "end_date": "2024-12-31",
        "year": "2024",
        "month": "12"
    }
}
```

### 2. Reports Summary

**Endpoint**: `GET /admin/reports/summary`

**Description**: Soo qaad summary statistics for different time periods

**Headers**:
```
Authorization: Bearer <admin_token>
```

**Response** (200):
```json
{
    "current_year": {
        "year": 2024,
        "translations": 1500,
        "users": 150
    },
    "monthly_stats": [
        {
            "month": 1,
            "month_name": "January",
            "translations": 120,
            "users": 25
        }
    ],
    "yearly_stats": [
        {
            "year": 2024,
            "translations": 1500,
            "users": 150
        },
        {
            "year": 2023,
            "translations": 1200,
            "users": 120
        }
    ]
}
```

### 3. Export Translations Report

**Endpoint**: `GET /admin/reports/translations/export`

**Description**: Export translations report as CSV file

**Query Parameters**: Same as translations report

**Headers**:
```
Authorization: Bearer <admin_token>
```

**Response**: CSV file download

### 4. Dashboard Statistics

**Endpoint**: `GET /admin/dashboard`

**Description**: Soo qaad dashboard overview statistics

**Headers**:
```
Authorization: Bearer <admin_token>
```

**Response** (200):
```json
{
    "total_users": 150,
    "active_users_today": 25,
    "suspended_users": 5,
    "translations_today": 50,
    "translations_week": 300,
    "translations_month": 1200,
    "total_favorites": 500,
    "recent_activity": [...],
    "top_users_month": [...],
    "top_users_week": [...]
}
```

### 5. Analytics

**Endpoint**: `GET /admin/analytics`

**Description**: Soo qaad detailed analytics and usage patterns

**Headers**:
```
Authorization: Bearer <admin_token>
```

**Response** (200):
```json
{
    "translation_volume": {
        "today": 50,
        "this_week": 300,
        "this_month": 1200
    },
    "user_engagement": {
        "daily_active_users": 25,
        "weekly_active_users": 80,
        "monthly_active_users": 150
    },
    "popular_features": {
        "favorites_used": 500,
        "history_accessed": 1200,
        "voice_input_used": 200
    },
    "usage_patterns": [...],
    "user_retention": [...]
}
```

## Usage Examples

### JavaScript/Frontend

```javascript
// Get translations report for current month
const getTranslationsReport = async (filters = {}) => {
    const params = new URLSearchParams(filters);
    const response = await fetch(`/admin/reports/translations?${params}`, {
        headers: {
            'Authorization': `Bearer ${adminToken}`
        }
    });
    
    if (response.ok) {
        const data = await response.json();
        console.log(`Found ${data.total} translations`);
        return data;
    } else {
        console.error('Failed to get translations report');
        return null;
    }
};

// Get report for specific year
const yearReport = await getTranslationsReport({ year: '2024' });

// Get report for specific year and month
const monthReport = await getTranslationsReport({ 
    year: '2024', 
    month: '12' 
});

// Get report for custom date range
const customReport = await getTranslationsReport({
    start_date: '2024-01-01',
    end_date: '2024-12-31'
});

// Export translations report
const exportReport = async (filters = {}) => {
    const params = new URLSearchParams(filters);
    const response = await fetch(`/admin/reports/translations/export?${params}`, {
        headers: {
            'Authorization': `Bearer ${adminToken}`
        }
    });
    
    if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        
        // Create download link
        const a = document.createElement('a');
        a.href = url;
        a.download = `translations_report_${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
        
        URL.revokeObjectURL(url);
    }
};
```

### Python

```python
import requests

def get_translations_report(admin_token, filters=None):
    """Get translations report with filters"""
    if filters is None:
        filters = {}
    
    url = "http://localhost:5000/admin/reports/translations"
    headers = {
        "Authorization": f"Bearer {admin_token}"
    }
    
    response = requests.get(url, params=filters, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None

def export_translations_report(admin_token, filters=None):
    """Export translations report as CSV"""
    if filters is None:
        filters = {}
    
    url = "http://localhost:5000/admin/reports/translations/export"
    headers = {
        "Authorization": f"Bearer {admin_token}"
    }
    
    response = requests.get(url, params=filters, headers=headers)
    
    if response.status_code == 200:
        # Save CSV file
        filename = f"translations_report_{datetime.now().strftime('%Y%m%d')}.csv"
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"✅ Report exported: {filename}")
        return filename
    else:
        print(f"❌ Export failed: {response.status_code}")
        return None

# Usage examples
admin_token = "your_admin_token_here"

# Get current month report
current_month = get_translations_report(admin_token)

# Get specific year report
year_2024 = get_translations_report(admin_token, {"year": "2024"})

# Get specific month report
december_2024 = get_translations_report(admin_token, {
    "year": "2024",
    "month": "12"
})

# Get custom date range
custom_range = get_translations_report(admin_token, {
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
})

# Export report
export_translations_report(admin_token, {"year": "2024", "month": "12"})
```

### cURL

```bash
# Get translations report for current month
curl -X GET "http://localhost:5000/admin/reports/translations" \
  -H "Authorization: Bearer your_admin_token_here"

# Get translations report for specific year
curl -X GET "http://localhost:5000/admin/reports/translations?year=2024" \
  -H "Authorization: Bearer your_admin_token_here"

# Get translations report for specific year and month
curl -X GET "http://localhost:5000/admin/reports/translations?year=2024&month=12" \
  -H "Authorization: Bearer your_admin_token_here"

# Get translations report for custom date range
curl -X GET "http://localhost:5000/admin/reports/translations?start_date=2024-01-01&end_date=2024-12-31" \
  -H "Authorization: Bearer your_admin_token_here"

# Export translations report
curl -X GET "http://localhost:5000/admin/reports/translations/export?year=2024&month=12" \
  -H "Authorization: Bearer your_admin_token_here" \
  --output "translations_report_2024_12.csv"

# Get reports summary
curl -X GET "http://localhost:5000/admin/reports/summary" \
  -H "Authorization: Bearer your_admin_token_here"

# Get dashboard statistics
curl -X GET "http://localhost:5000/admin/dashboard" \
  -H "Authorization: Bearer your_admin_token_here"

# Get analytics
curl -X GET "http://localhost:5000/admin/analytics" \
  -H "Authorization: Bearer your_admin_token_here"
```

## Filtering Options

### Date Filters

| Parameter | Format | Example | Description |
|-----------|--------|---------|-------------|
| `year` | YYYY | `2024` | Specific year |
| `month` | 1-12 | `12` | Specific month |
| `start_date` | YYYY-MM-DD | `2024-01-01` | Custom start date |
| `end_date` | YYYY-MM-DD | `2024-12-31` | Custom end date |

### Pagination

| Parameter | Default | Description |
|-----------|---------|-------------|
| `page` | 1 | Page number |
| `limit` | 50 | Items per page |

### Filter Combinations

```javascript
// Current month (default)
GET /admin/reports/translations

// Specific year
GET /admin/reports/translations?year=2024

// Specific year and month
GET /admin/reports/translations?year=2024&month=12

// Custom date range
GET /admin/reports/translations?start_date=2024-01-01&end_date=2024-12-31

// With pagination
GET /admin/reports/translations?year=2024&page=2&limit=25
```

## Report Types

### 1. Translations Report
- **Endpoint**: `/admin/reports/translations`
- **Description**: Detailed list of translations with user information
- **Features**: Date filtering, pagination, statistics
- **Use case**: Detailed analysis of translation activity

### 2. Reports Summary
- **Endpoint**: `/admin/reports/summary`
- **Description**: High-level statistics for different time periods
- **Features**: Current year, monthly stats, yearly comparison
- **Use case**: Overview and trend analysis

### 3. Export Functionality
- **Endpoint**: `/admin/reports/translations/export`
- **Description**: CSV export of translations data
- **Features**: Same filtering as translations report
- **Use case**: Data export for external analysis

### 4. Dashboard Statistics
- **Endpoint**: `/admin/dashboard`
- **Description**: Real-time dashboard overview
- **Features**: Today's stats, recent activity, top users
- **Use case**: Daily monitoring and quick insights

### 5. Analytics
- **Endpoint**: `/admin/analytics`
- **Description**: Detailed analytics and usage patterns
- **Features**: User engagement, usage patterns, retention
- **Use case**: Deep analysis and strategic insights

## Data Structure

### Translation Record
```json
{
    "_id": "64f1a2b3c4d5e6f7g8h9i0j1",
    "user_name": "Ahmed Hassan",
    "user_email": "ahmed@example.com",
    "timestamp": "2024-12-01T10:30:00Z",
    "original_text": "Hello world",
    "translated_text": "Salaam dunida",
    "source_language": "English",
    "target_language": "Somali"
}
```

### Statistics Object
```json
{
    "total_translations": 150,
    "unique_users": 25,
    "language_pairs": [
        {
            "_id": {
                "source": "English",
                "target": "Somali"
            },
            "count": 120
        }
    ]
}
```

### Monthly Statistics
```json
{
    "month": 12,
    "month_name": "December",
    "translations": 150,
    "users": 25
}
```

## Error Handling

### Common Errors

1. **Unauthorized** (401):
   ```json
   {
     "error": "Invalid or missing token"
   }
   ```

2. **Forbidden** (403):
   ```json
   {
     "error": "Admin access required"
   }
   ```

3. **Invalid Date Format** (400):
   ```json
   {
     "error": "Invalid date format. Use YYYY-MM-DD"
   }
   ```

4. **Invalid Year/Month** (400):
   ```json
   {
     "error": "Invalid year or month"
   }
   ```

### Error Handling Example

```javascript
const getReport = async (filters) => {
    try {
        const response = await fetch(`/admin/reports/translations?${new URLSearchParams(filters)}`, {
            headers: {
                'Authorization': `Bearer ${adminToken}`
            }
        });
        
        if (response.status === 401) {
            console.error('Unauthorized - Check your token');
            return null;
        } else if (response.status === 403) {
            console.error('Forbidden - Admin access required');
            return null;
        } else if (response.status === 400) {
            const error = await response.json();
            console.error('Bad request:', error.error);
            return null;
        } else if (!response.ok) {
            console.error('Request failed:', response.status);
            return null;
        }
        
        return await response.json();
        
    } catch (error) {
        console.error('Network error:', error);
        return null;
    }
};
```

## Testing

### Run Tests
```bash
python test_admin_reports.py
```

### Test Results
```
=== Admin Reports System Tests ===

1. Testing current month report...
✅ Current month report: 150 translations
   Unique users: 25
   Language pairs: 3

2. Testing specific year report...
✅ Year 2024 report: 1200 translations

3. Testing specific year and month report...
✅ 2024-12 report: 150 translations

4. Testing custom date range report...
✅ Custom date range report: 300 translations
   Date range: 2024-11-01 to 2024-12-01

Testing reports summary...
✅ Reports summary:
   Current year: 1200 translations, 150 users
   Monthly stats: 12 months
   Yearly stats: 5 years
   Top 3 months:
     December: 150 translations
     November: 140 translations
     October: 130 translations
```

## Security Considerations

### Authentication
- All endpoints require valid admin JWT token
- Tokens must have admin role
- Tokens expire after 2 hours

### Authorization
- Only admin users can access reporting endpoints
- User data is anonymized in reports
- Sensitive information is filtered out

### Rate Limiting
- Consider implementing rate limiting for large reports
- Pagination helps manage data volume
- Export functionality may have size limits

## Performance Tips

### Optimization
- Use pagination for large datasets
- Implement caching for summary statistics
- Consider database indexing for date queries

### Best Practices
- Use appropriate date filters to limit data
- Export large datasets instead of loading in memory
- Implement proper error handling

## Support

Haddii aad u baahan tahay caawimaad dheeraad ah:
- Check authentication and authorization
- Verify date format and parameters
- Test with smaller date ranges first
- Check API documentation

---

**Admin reporting system-ka cusub wuxuu si sax ah u shaqeynaya!** 📊✅
