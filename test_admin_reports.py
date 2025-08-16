import requests
import json
from datetime import datetime, timedelta

# Test configuration
BASE_URL = "http://localhost:5000"
ADMIN_TOKEN = "your_admin_token_here"  # Replace with actual admin token

def test_translations_report():
    """Test translations report with different date filters"""
    print("Testing translations report...")
    
    headers = {
        "Authorization": f"Bearer {ADMIN_TOKEN}"
    }
    
    # Test 1: Current month (default)
    print("\n1. Testing current month report...")
    response = requests.get(f"{BASE_URL}/admin/reports/translations", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Current month report: {data['total']} translations")
        print(f"   Unique users: {data['statistics']['unique_users']}")
        print(f"   Language pairs: {len(data['statistics']['language_pairs'])}")
    else:
        print(f"❌ Current month report failed: {response.status_code}")
        print(f"   Error: {response.text}")
    
    # Test 2: Specific year
    print("\n2. Testing specific year report...")
    current_year = datetime.now().year
    response = requests.get(
        f"{BASE_URL}/admin/reports/translations?year={current_year}", 
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Year {current_year} report: {data['total']} translations")
    else:
        print(f"❌ Year report failed: {response.status_code}")
    
    # Test 3: Specific year and month
    print("\n3. Testing specific year and month report...")
    current_month = datetime.now().month
    response = requests.get(
        f"{BASE_URL}/admin/reports/translations?year={current_year}&month={current_month}", 
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ {current_year}-{current_month:02d} report: {data['total']} translations")
    else:
        print(f"❌ Year-month report failed: {response.status_code}")
    
    # Test 4: Custom date range
    print("\n4. Testing custom date range report...")
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    response = requests.get(
        f"{BASE_URL}/admin/reports/translations?start_date={start_date}&end_date={end_date}", 
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Custom date range report: {data['total']} translations")
        print(f"   Date range: {start_date} to {end_date}")
    else:
        print(f"❌ Custom date range report failed: {response.status_code}")

def test_reports_summary():
    """Test reports summary endpoint"""
    print("\n\nTesting reports summary...")
    
    headers = {
        "Authorization": f"Bearer {ADMIN_TOKEN}"
    }
    
    response = requests.get(f"{BASE_URL}/admin/reports/summary", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Reports summary:")
        print(f"   Current year: {data['current_year']['translations']} translations, {data['current_year']['users']} users")
        print(f"   Monthly stats: {len(data['monthly_stats'])} months")
        print(f"   Yearly stats: {len(data['yearly_stats'])} years")
        
        # Show top months
        top_months = sorted(data['monthly_stats'], key=lambda x: x['translations'], reverse=True)[:3]
        print(f"   Top 3 months:")
        for month in top_months:
            print(f"     {month['month_name']}: {month['translations']} translations")
    else:
        print(f"❌ Reports summary failed: {response.status_code}")
        print(f"   Error: {response.text}")

def test_export_translations():
    """Test translations export functionality"""
    print("\n\nTesting translations export...")
    
    headers = {
        "Authorization": f"Bearer {ADMIN_TOKEN}"
    }
    
    # Test export for current month
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    response = requests.get(
        f"{BASE_URL}/admin/reports/translations/export?year={current_year}&month={current_month}", 
        headers=headers
    )
    
    if response.status_code == 200:
        content_type = response.headers.get('Content-Type', '')
        content_disposition = response.headers.get('Content-Disposition', '')
        
        print(f"✅ Export successful:")
        print(f"   Content-Type: {content_type}")
        print(f"   Content-Disposition: {content_disposition}")
        print(f"   File size: {len(response.content)} bytes")
        
        # Check if it's actually CSV
        if 'text/csv' in content_type:
            print(f"   ✅ Valid CSV file")
        else:
            print(f"   ⚠️  Not a CSV file")
    else:
        print(f"❌ Export failed: {response.status_code}")
        print(f"   Error: {response.text}")

def test_dashboard_stats():
    """Test dashboard statistics"""
    print("\n\nTesting dashboard statistics...")
    
    headers = {
        "Authorization": f"Bearer {ADMIN_TOKEN}"
    }
    
    response = requests.get(f"{BASE_URL}/admin/dashboard", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Dashboard stats:")
        print(f"   Total users: {data['total_users']}")
        print(f"   Active users today: {data['active_users_today']}")
        print(f"   Suspended users: {data['suspended_users']}")
        print(f"   Translations today: {data['translations_today']}")
        print(f"   Translations this week: {data['translations_week']}")
        print(f"   Translations this month: {data['translations_month']}")
        print(f"   Total favorites: {data['total_favorites']}")
        print(f"   Recent activity: {len(data['recent_activity'])} items")
        print(f"   Top users month: {len(data['top_users_month'])} users")
        print(f"   Top users week: {len(data['top_users_week'])} users")
    else:
        print(f"❌ Dashboard stats failed: {response.status_code}")
        print(f"   Error: {response.text}")

def test_analytics():
    """Test analytics endpoint"""
    print("\n\nTesting analytics...")
    
    headers = {
        "Authorization": f"Bearer {ADMIN_TOKEN}"
    }
    
    response = requests.get(f"{BASE_URL}/admin/analytics", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Analytics:")
        print(f"   Translation volume:")
        print(f"     Today: {data['translation_volume']['today']}")
        print(f"     This week: {data['translation_volume']['this_week']}")
        print(f"     This month: {data['translation_volume']['this_month']}")
        print(f"   User engagement:")
        print(f"     Daily active users: {data['user_engagement']['daily_active_users']}")
        print(f"     Weekly active users: {data['user_engagement']['weekly_active_users']}")
        print(f"     Monthly active users: {data['user_engagement']['monthly_active_users']}")
        print(f"   Popular features:")
        print(f"     Favorites used: {data['popular_features']['favorites_used']}")
        print(f"     History accessed: {data['popular_features']['history_accessed']}")
        print(f"     Voice input used: {data['popular_features']['voice_input_used']}")
        print(f"   Usage patterns: {len(data['usage_patterns'])} days")
        print(f"   User retention: {len(data['user_retention'])} weeks")
    else:
        print(f"❌ Analytics failed: {response.status_code}")
        print(f"   Error: {response.text}")

def test_user_management():
    """Test user management endpoints"""
    print("\n\nTesting user management...")
    
    headers = {
        "Authorization": f"Bearer {ADMIN_TOKEN}"
    }
    
    # Test get all users
    response = requests.get(f"{BASE_URL}/admin/users", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ User management:")
        print(f"   Total users: {data['total']}")
        print(f"   Users on page: {len(data['users'])}")
        print(f"   Current page: {data['page']}")
        print(f"   Total pages: {data['pages']}")
        
        # Show first user details
        if data['users']:
            first_user = data['users'][0]
            print(f"   First user:")
            print(f"     Name: {first_user.get('full_name', 'N/A')}")
            print(f"     Email: {first_user.get('email', 'N/A')}")
            print(f"     Role: {first_user.get('role', 'N/A')}")
            print(f"     Translations: {first_user.get('translations_count', 0)}")
            print(f"     Favorites: {first_user.get('favorites_count', 0)}")
    else:
        print(f"❌ User management failed: {response.status_code}")
        print(f"   Error: {response.text}")

def main():
    print("=== Admin Reports System Tests ===\n")
    
    # Test 1: Translations report
    test_translations_report()
    
    # Test 2: Reports summary
    test_reports_summary()
    
    # Test 3: Export functionality
    test_export_translations()
    
    # Test 4: Dashboard stats
    test_dashboard_stats()
    
    # Test 5: Analytics
    test_analytics()
    
    # Test 6: User management
    test_user_management()
    
    print("\n=== API Usage Examples ===")
    print("1. Get translations report for current month:")
    print("   GET /admin/reports/translations")
    
    print("\n2. Get translations report for specific year:")
    print("   GET /admin/reports/translations?year=2024")
    
    print("\n3. Get translations report for specific year and month:")
    print("   GET /admin/reports/translations?year=2024&month=12")
    
    print("\n4. Get translations report for custom date range:")
    print("   GET /admin/reports/translations?start_date=2024-01-01&end_date=2024-12-31")
    
    print("\n5. Export translations report:")
    print("   GET /admin/reports/translations/export?year=2024&month=12")
    
    print("\n6. Get reports summary:")
    print("   GET /admin/reports/summary")
    
    print("\n7. Get dashboard statistics:")
    print("   GET /admin/dashboard")
    
    print("\n8. Get analytics:")
    print("   GET /admin/analytics")
    
    print("\n9. Get all users:")
    print("   GET /admin/users?page=1&limit=10")
    
    print("\n=== Filtering Options ===")
    print("📅 Date Filters:")
    print("  - year: Specific year (e.g., 2024)")
    print("  - month: Specific month (1-12)")
    print("  - start_date: Custom start date (YYYY-MM-DD)")
    print("  - end_date: Custom end date (YYYY-MM-DD)")
    
    print("\n📊 Pagination:")
    print("  - page: Page number (default: 1)")
    print("  - limit: Items per page (default: 50)")
    
    print("\n📈 Report Types:")
    print("  - /admin/reports/translations: Detailed translations report")
    print("  - /admin/reports/summary: Summary statistics")
    print("  - /admin/reports/translations/export: CSV export")
    print("  - /admin/dashboard: Dashboard overview")
    print("  - /admin/analytics: Detailed analytics")
    
    print("\nNote: Replace ADMIN_TOKEN with a valid admin token before running tests.")

if __name__ == "__main__":
    main()
