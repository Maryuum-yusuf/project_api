from flask import Blueprint, jsonify, request
from bson import ObjectId
from pymongo import MongoClient
from datetime import datetime, timedelta
from middlewares.auth_decorator import admin_required
import pytz
from flask import make_response
import calendar

client = MongoClient("mongodb://localhost:27017/")
db = client["somali_translator_db"]
users = db["users"]
translations = db["translations"]
favorites = db["favorites"]
voice_translations = db["voice_translations"]

admin_routes = Blueprint("admin_routes", __name__)

# Dashboard Analytics
@admin_routes.route("/admin/dashboard", methods=["GET"])
@admin_required
def get_dashboard_stats():
    somalia_tz = pytz.timezone('Africa/Mogadishu')
    now = datetime.now(somalia_tz)
    
    # Time ranges
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=now.weekday())
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # User statistics
    total_users = users.count_documents({})
    
    # Active users today - count unique users who made translations today
    # This is more accurate than last_login since we know they actually used the app
    active_users_today = len(set(
        str(translation.get("user_id")) 
        for translation in translations.find({
            "timestamp": {"$gte": today_start.isoformat()}
        })
    ))
    
    suspended_users = users.count_documents({"is_suspended": True})
    
    # Translation statistics
    translations_today = translations.count_documents({
        "timestamp": {"$gte": today_start.isoformat()}
    })
    translations_week = translations.count_documents({
        "timestamp": {"$gte": week_start.isoformat()}
    })
    translations_month = translations.count_documents({
        "timestamp": {"$gte": month_start.isoformat()}
    })
    
    # Favorites statistics
    total_favorites = favorites.count_documents({})
    
    # Recent Activity - Get last 10 translations with user details
    recent_translations = list(translations.find().sort("timestamp", -1).limit(10))
    recent_activity = []
    
    for translation in recent_translations:
        user_id = translation.get("user_id")
        user_info = None
        
        # Debug: Print user_id to see what we're getting
        print(f"Translation user_id: {user_id}, type: {type(user_id)}")
        
        # Handle different user_id formats
        if user_id:
            try:
                # If user_id is already ObjectId
                if isinstance(user_id, ObjectId):
                    user_info = users.find_one({"_id": user_id})
                # If user_id is string, convert to ObjectId
                elif isinstance(user_id, str):
                    user_info = users.find_one({"_id": ObjectId(user_id)})
                # If user_id is already a dict with _id
                elif isinstance(user_id, dict) and "_id" in user_id:
                    user_info = users.find_one({"_id": ObjectId(user_id["_id"])})
            except Exception as e:
                print(f"Error finding user for translation: {e}")
                user_info = None
        
        # Get user name or use email as fallback
        user_name = "Guest User"  # Change from "Unknown User" to "Guest User"
        user_email = ""
        
        if user_info:
            user_name = user_info.get("full_name", "")
            user_email = user_info.get("email", "")
            
            # If no full_name, use email
            if not user_name and user_email:
                user_name = user_email.split('@')[0]  # Use part before @
            # If still no name, use first letter of email
            elif not user_name:
                user_name = user_email[0].upper() if user_email else "G"
        
        # Debug: Print what we found
        print(f"Found user: {user_name} ({user_email})")
        
        recent_activity.append({
            "user_name": user_name,
            "user_email": user_email,
            "timestamp": translation.get("timestamp", ""),
            "original_text": translation.get("original_text", ""),
            "translated_text": translation.get("translated_text", ""),
            "source_language": translation.get("source_language", "Unknown"),
            "target_language": translation.get("target_language", "Unknown")
        })
    
    # Top users by translations this month
    pipeline = [
        {"$match": {"timestamp": {"$gte": month_start.isoformat()}}},
        {"$group": {"_id": "$user_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    top_users_month = list(translations.aggregate(pipeline))
    
    # Top users by translations this week
    pipeline = [
        {"$match": {"timestamp": {"$gte": week_start.isoformat()}}},
        {"$group": {"_id": "$user_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    top_users_week = list(translations.aggregate(pipeline))
    
    # Get user details for top users
    def get_user_details(user_list):
        user_details = []
        for user in user_list:
            user_id = user["_id"]
            user_info = None
            
            # Debug: Print user_id to see what we're getting
            print(f"Top user user_id: {user_id}, type: {type(user_id)}")
            
            # Handle different user_id formats
            if user_id:
                try:
                    # If user_id is already ObjectId
                    if isinstance(user_id, ObjectId):
                        user_info = users.find_one({"_id": user_id})
                    # If user_id is string, convert to ObjectId
                    elif isinstance(user_id, str):
                        user_info = users.find_one({"_id": ObjectId(user_id)})
                    # If user_id is already a dict with _id
                    elif isinstance(user_id, dict) and "_id" in user_id:
                        user_info = users.find_one({"_id": ObjectId(user_id["_id"])})
                except Exception as e:
                    print(f"Error finding top user: {e}")
                    user_info = None
            
            # Get user name or use email as fallback
            user_name = "Anonymous User"  # Change to "Anonymous User"
            user_email = ""
            
            if user_info:
                user_name = user_info.get("full_name", "")
                user_email = user_info.get("email", "")
                
                # If no full_name, use email
                if not user_name and user_email:
                    user_name = user_email.split('@')[0]  # Use part before @
                # If still no name, use first letter of email
                elif not user_name:
                    user_name = user_email[0].upper() if user_email else "A"
            
            # Debug: Print what we found
            print(f"Found top user: {user_name} ({user_email})")
            
            user_details.append({
                "user_id": str(user_id),
                "full_name": user_name,
                "email": user_email,
                "translation_count": user["count"]
            })
        return user_details
    
    return jsonify({
        "total_users": total_users,
        "active_users_today": active_users_today,
        "suspended_users": suspended_users,
        "translations_today": translations_today,
        "translations_week": translations_week,
        "translations_month": translations_month,
        "total_favorites": total_favorites,
        "recent_activity": recent_activity,
        "top_users_month": get_user_details(top_users_month),
        "top_users_week": get_user_details(top_users_week)
    })

# Comprehensive Reporting System
@admin_routes.route("/admin/reports/translations", methods=["GET"])
@admin_required
def get_translations_report():
    """Get detailed translations report with date filtering"""
    
    # Get query parameters
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    year = request.args.get("year")
    month = request.args.get("month")
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 50))
    skip = (page - 1) * limit
    
    somalia_tz = pytz.timezone('Africa/Mogadishu')
    now = datetime.now(somalia_tz)
    
    # Build date filter
    date_filter = {}
    
    if start_date and end_date:
        # Custom date range
        try:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            date_filter = {
                "timestamp": {
                    "$gte": start_dt.isoformat(),
                    "$lte": end_dt.isoformat()
                }
            }
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    
    elif year and month:
        # Specific year and month
        try:
            year = int(year)
            month = int(month)
            start_dt = datetime(year, month, 1, tzinfo=somalia_tz)
            if month == 12:
                end_dt = datetime(year + 1, 1, 1, tzinfo=somalia_tz)
            else:
                end_dt = datetime(year, month + 1, 1, tzinfo=somalia_tz)
            date_filter = {
                "timestamp": {
                    "$gte": start_dt.isoformat(),
                    "$lt": end_dt.isoformat()
                }
            }
        except ValueError:
            return jsonify({"error": "Invalid year or month"}), 400
    
    elif year:
        # Specific year
        try:
            year = int(year)
            start_dt = datetime(year, 1, 1, tzinfo=somalia_tz)
            end_dt = datetime(year + 1, 1, 1, tzinfo=somalia_tz)
            date_filter = {
                "timestamp": {
                    "$gte": start_dt.isoformat(),
                    "$lt": end_dt.isoformat()
                }
            }
        except ValueError:
            return jsonify({"error": "Invalid year"}), 400
    
    else:
        # Default: current month
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if now.month == 12:
            next_month = now.replace(year=now.year + 1, month=1, day=1)
        else:
            next_month = now.replace(month=now.month + 1, day=1)
        
        date_filter = {
            "timestamp": {
                "$gte": month_start.isoformat(),
                "$lt": next_month.isoformat()
            }
        }
    
    # Get translations with filter
    total_translations = translations.count_documents(date_filter)
    translations_list = list(translations.find(date_filter).skip(skip).limit(limit).sort("timestamp", -1))
    
    # Process translations and get user details
    processed_translations = []
    for translation in translations_list:
        user_id = translation.get("user_id")
        user_info = None
        
        if user_id:
            try:
                if isinstance(user_id, ObjectId):
                    user_info = users.find_one({"_id": user_id})
                elif isinstance(user_id, str):
                    user_info = users.find_one({"_id": ObjectId(user_id)})
            except:
                user_info = None
        
        user_name = "Guest User"
        user_email = ""
        
        if user_info:
            user_name = user_info.get("full_name", "")
            user_email = user_info.get("email", "")
            if not user_name and user_email:
                user_name = user_email.split('@')[0]
        
        processed_translations.append({
            "_id": str(translation["_id"]),
            "user_name": user_name,
            "user_email": user_email,
            "timestamp": translation.get("timestamp", ""),
            "original_text": translation.get("original_text", ""),
            "translated_text": translation.get("translated_text", ""),
            "source_language": translation.get("source_language", "Unknown"),
            "target_language": translation.get("target_language", "Unknown")
        })
    
    # Calculate statistics
    unique_users = len(set(
        str(translation.get("user_id")) 
        for translation in translations.find(date_filter)
    ))
    
    # Language pair statistics
    pipeline = [
        {"$match": date_filter},
        {"$group": {
            "_id": {
                "source": "$source_language",
                "target": "$target_language"
            },
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}}
    ]
    language_stats = list(translations.aggregate(pipeline))
    
    return jsonify({
        "translations": processed_translations,
        "total": total_translations,
        "page": page,
        "limit": limit,
        "pages": (total_translations + limit - 1) // limit,
        "statistics": {
            "total_translations": total_translations,
            "unique_users": unique_users,
            "language_pairs": language_stats
        },
        "date_filter": {
            "start_date": start_date,
            "end_date": end_date,
            "year": year,
            "month": month
        }
    })

@admin_routes.route("/admin/reports/translations/export", methods=["GET"])
@admin_required
def export_translations_report():
    """Export translations report as CSV"""
    
    # Get query parameters
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    year = request.args.get("year")
    month = request.args.get("month")
    
    somalia_tz = pytz.timezone('Africa/Mogadishu')
    now = datetime.now(somalia_tz)
    
    # Build date filter (same logic as above)
    date_filter = {}
    
    if start_date and end_date:
        try:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            date_filter = {
                "timestamp": {
                    "$gte": start_dt.isoformat(),
                    "$lte": end_dt.isoformat()
                }
            }
        except ValueError:
            return jsonify({"error": "Invalid date format"}), 400
    
    elif year and month:
        try:
            year = int(year)
            month = int(month)
            start_dt = datetime(year, month, 1, tzinfo=somalia_tz)
            if month == 12:
                end_dt = datetime(year + 1, 1, 1, tzinfo=somalia_tz)
            else:
                end_dt = datetime(year, month + 1, 1, tzinfo=somalia_tz)
            date_filter = {
                "timestamp": {
                    "$gte": start_dt.isoformat(),
                    "$lt": end_dt.isoformat()
                }
            }
        except ValueError:
            return jsonify({"error": "Invalid year or month"}), 400
    
    elif year:
        try:
            year = int(year)
            start_dt = datetime(year, 1, 1, tzinfo=somalia_tz)
            end_dt = datetime(year + 1, 1, 1, tzinfo=somalia_tz)
            date_filter = {
                "timestamp": {
                    "$gte": start_dt.isoformat(),
                    "$lt": end_dt.isoformat()
                }
            }
        except ValueError:
            return jsonify({"error": "Invalid year"}), 400
    
    else:
        # Default: current month
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if now.month == 12:
            next_month = now.replace(year=now.year + 1, month=1, day=1)
        else:
            next_month = now.replace(month=now.month + 1, day=1)
        
        date_filter = {
            "timestamp": {
                "$gte": month_start.isoformat(),
                "$lt": next_month.isoformat()
            }
        }
    
    # Get all translations for the period
    all_translations = list(translations.find(date_filter).sort("timestamp", -1))
    
    # Create CSV content
    csv_content = "User Name,User Email,Timestamp,Original Text,Translated Text,Source Language,Target Language\n"
    
    for translation in all_translations:
        user_id = translation.get("user_id")
        user_info = None
        
        if user_id:
            try:
                if isinstance(user_id, ObjectId):
                    user_info = users.find_one({"_id": user_id})
                elif isinstance(user_id, str):
                    user_info = users.find_one({"_id": ObjectId(user_id)})
            except:
                user_info = None
        
        user_name = "Guest User"
        user_email = ""
        
        if user_info:
            user_name = user_info.get("full_name", "").replace('"', '""')
            user_email = user_info.get("email", "").replace('"', '""')
            if not user_name and user_email:
                user_name = user_email.split('@')[0].replace('"', '""')
        
        timestamp = translation.get("timestamp", "").replace('"', '""')
        original_text = translation.get("original_text", "").replace('"', '""')
        translated_text = translation.get("translated_text", "").replace('"', '""')
        source_lang = translation.get("source_language", "Unknown").replace('"', '""')
        target_lang = translation.get("target_language", "Unknown").replace('"', '""')
        
        csv_content += f'"{user_name}","{user_email}","{timestamp}","{original_text}","{translated_text}","{source_lang}","{target_lang}"\n'
    
    # Return CSV file
    response = make_response(csv_content)
    response.headers['Content-Type'] = 'text/csv'
    
    # Generate filename based on filter
    if year and month:
        filename = f"translations_report_{year}_{month:02d}.csv"
    elif year:
        filename = f"translations_report_{year}.csv"
    elif start_date and end_date:
        filename = f"translations_report_{start_date}_to_{end_date}.csv"
    else:
        filename = f"translations_report_{now.strftime('%Y_%m')}.csv"
    
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    
    return response

@admin_routes.route("/admin/reports/summary", methods=["GET"])
@admin_required
def get_reports_summary():
    """Get summary statistics for different time periods"""
    
    somalia_tz = pytz.timezone('Africa/Mogadishu')
    now = datetime.now(somalia_tz)
    
    # Current year statistics
    year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    year_end = year_start.replace(year=year_start.year + 1)
    
    year_translations = translations.count_documents({
        "timestamp": {
            "$gte": year_start.isoformat(),
            "$lt": year_end.isoformat()
        }
    })
    
    year_users = len(set(
        str(translation.get("user_id")) 
        for translation in translations.find({
            "timestamp": {
                "$gte": year_start.isoformat(),
                "$lt": year_end.isoformat()
            }
        })
    ))
    
    # Monthly statistics for current year
    monthly_stats = []
    for month in range(1, 13):
        month_start = year_start.replace(month=month)
        if month == 12:
            month_end = year_start.replace(year=year_start.year + 1, month=1)
        else:
            month_end = year_start.replace(month=month + 1)
        
        month_translations = translations.count_documents({
            "timestamp": {
                "$gte": month_start.isoformat(),
                "$lt": month_end.isoformat()
            }
        })
        
        month_users = len(set(
            str(translation.get("user_id")) 
            for translation in translations.find({
                "timestamp": {
                    "$gte": month_start.isoformat(),
                    "$lt": month_end.isoformat()
                }
            })
        ))
        
        monthly_stats.append({
            "month": month,
            "month_name": calendar.month_name[month],
            "translations": month_translations,
            "users": month_users
        })
    
    # Last 5 years summary
    yearly_stats = []
    for year_offset in range(5):
        year = now.year - year_offset
        year_start = now.replace(year=year, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        year_end = year_start.replace(year=year + 1)
        
        year_translations = translations.count_documents({
            "timestamp": {
                "$gte": year_start.isoformat(),
                "$lt": year_end.isoformat()
            }
        })
        
        year_users = len(set(
            str(translation.get("user_id")) 
            for translation in translations.find({
                "timestamp": {
                    "$gte": year_start.isoformat(),
                    "$lt": year_end.isoformat()
                }
            })
        ))
        
        yearly_stats.append({
            "year": year,
            "translations": year_translations,
            "users": year_users
        })
    
    return jsonify({
        "current_year": {
            "year": now.year,
            "translations": year_translations,
            "users": year_users
        },
        "monthly_stats": monthly_stats,
        "yearly_stats": yearly_stats
    })

# User Management
@admin_routes.route("/admin/users", methods=["GET"])
@admin_required
def get_all_users_admin():
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    skip = (page - 1) * limit
    
    # Get total count
    total_users = users.count_documents({})
    
    # Get users with pagination
    all_users = []
    for user in users.find().skip(skip).limit(limit).sort("created_at", -1):
        user["_id"] = str(user["_id"])
        user.pop("password", None)
        
        # Get user statistics
        user_id = user["_id"]
        translations_count = translations.count_documents({"user_id": ObjectId(user_id)})
        favorites_count = favorites.count_documents({"user_id": ObjectId(user_id)})
        
        user["translations_count"] = translations_count
        user["favorites_count"] = favorites_count
        all_users.append(user)
    
    return jsonify({
        "users": all_users,
        "total": total_users,
        "page": page,
        "limit": limit,
        "pages": (total_users + limit - 1) // limit
    })

@admin_routes.route("/admin/users/<user_id>/suspend", methods=["POST"])
@admin_required
def suspend_user(user_id):
    result = users.update_one(
        {"_id": ObjectId(user_id)}, 
        {"$set": {"is_suspended": True}}
    )
    if result.matched_count == 0:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"message": "User suspended successfully"})

@admin_routes.route("/admin/users/<user_id>/unsuspend", methods=["POST"])
@admin_required
def unsuspend_user(user_id):
    result = users.update_one(
        {"_id": ObjectId(user_id)}, 
        {"$set": {"is_suspended": False}}
    )
    if result.matched_count == 0:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"message": "User unsuspended successfully"})

@admin_routes.route("/admin/users/<user_id>/stats", methods=["GET"])
@admin_required
def get_user_stats(user_id):
    user = users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Get user's translations
    user_translations = list(translations.find({"user_id": ObjectId(user_id)}).sort("timestamp", -1))
    for trans in user_translations:
        trans["_id"] = str(trans["_id"])
        if isinstance(trans.get("user_id"), ObjectId):
            trans["user_id"] = str(trans["user_id"])
    
    # Get user's favorites
    user_favorites = list(favorites.find({"user_id": ObjectId(user_id)}).sort("timestamp", -1))
    for fav in user_favorites:
        fav["_id"] = str(fav["_id"])
        if isinstance(fav.get("user_id"), ObjectId):
            fav["user_id"] = str(fav["user_id"])
        if isinstance(fav.get("translation_id"), ObjectId):
            fav["translation_id"] = str(fav["translation_id"])
    
    # Calculate statistics
    total_translations = len(user_translations)
    total_favorites = len(user_favorites)
    
    # Recent activity (last 7 days) - count translations made in last 7 days
    somalia_tz = pytz.timezone('Africa/Mogadishu')
    week_ago = datetime.now(somalia_tz) - timedelta(days=7)
    recent_translations = len([t for t in user_translations if t.get("timestamp", "") >= week_ago.isoformat()])
    
    return jsonify({
        "user": {
            "_id": str(user["_id"]),
            "full_name": user.get("full_name", ""),
            "email": user.get("email", ""),
            "role": user.get("role", "user"),
            "is_suspended": user.get("is_suspended", False),
            "created_at": user.get("created_at", ""),
            "last_login": user.get("last_login", "")
        },
        "stats": {
            "total_translations": total_translations,
            "total_favorites": total_favorites,
            "recent_translations": recent_translations
        },
        "translations": user_translations[:10],  # Last 10 translations
        "favorites": user_favorites[:10]  # Last 10 favorites
    })

# Analytics and Reports
@admin_routes.route("/admin/analytics", methods=["GET"])
@admin_required
def get_analytics():
    somalia_tz = pytz.timezone('Africa/Mogadishu')
    now = datetime.now(somalia_tz)
    
    # Time ranges
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=now.weekday())
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Translation volume
    translations_today = translations.count_documents({
        "timestamp": {"$gte": today_start.isoformat()}
    })
    translations_week = translations.count_documents({
        "timestamp": {"$gte": week_start.isoformat()}
    })
    translations_month = translations.count_documents({
        "timestamp": {"$gte": month_start.isoformat()}
    })
    
    # User engagement - count unique users who made translations
    daily_active_users = len(set(
        str(translation.get("user_id")) 
        for translation in translations.find({
            "timestamp": {"$gte": today_start.isoformat()}
        })
    ))
    
    weekly_active_users = len(set(
        str(translation.get("user_id")) 
        for translation in translations.find({
            "timestamp": {"$gte": week_start.isoformat()}
        })
    ))
    
    monthly_active_users = len(set(
        str(translation.get("user_id")) 
        for translation in translations.find({
            "timestamp": {"$gte": month_start.isoformat()}
        })
    ))
    
    # Popular features
    favorites_used = favorites.count_documents({})
    history_accessed = translations.count_documents({})
    voice_input_used = voice_translations.count_documents({})
    
    # Usage patterns (daily for last 7 days)
    daily_usage = []
    for i in range(7):
        day_start = today_start - timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        count = translations.count_documents({
            "timestamp": {
                "$gte": day_start.isoformat(),
                "$lt": day_end.isoformat()
            }
        })
        daily_usage.append({
            "date": day_start.strftime("%Y-%m-%d"),
            "count": count
        })
    daily_usage.reverse()
    
    # User retention - count unique users per week
    retention_data = []
    for i in range(4):  # Last 4 weeks
        week_start_date = week_start - timedelta(weeks=i)
        week_end_date = week_start_date + timedelta(weeks=1)
        
        active_users = len(set(
            str(translation.get("user_id")) 
            for translation in translations.find({
                "timestamp": {
                    "$gte": week_start_date.isoformat(),
                    "$lt": week_end_date.isoformat()
                }
            })
        ))
        
        retention_data.append({
            "week": week_start_date.strftime("%Y-%m-%d"),
            "active_users": active_users
        })
    retention_data.reverse()
    
    return jsonify({
        "translation_volume": {
            "today": translations_today,
            "this_week": translations_week,
            "this_month": translations_month
        },
        "user_engagement": {
            "daily_active_users": daily_active_users,
            "weekly_active_users": weekly_active_users,
            "monthly_active_users": monthly_active_users
        },
        "popular_features": {
            "favorites_used": favorites_used,
            "history_accessed": history_accessed,
            "voice_input_used": voice_input_used
        },
        "usage_patterns": daily_usage,
        "user_retention": retention_data
    })

@admin_routes.route("/admin/analytics/export", methods=["GET"])
@admin_required
def export_analytics():
    try:
        somalia_tz = pytz.timezone('Africa/Mogadishu')
        now = datetime.now(somalia_tz)
        
        # Time ranges
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=now.weekday())
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Translation volume
        translations_today = translations.count_documents({
            "timestamp": {"$gte": today_start.isoformat()}
        })
        translations_week = translations.count_documents({
            "timestamp": {"$gte": week_start.isoformat()}
        })
        translations_month = translations.count_documents({
            "timestamp": {"$gte": month_start.isoformat()}
        })
        
        # User engagement
        daily_active_users = len(set(
            str(translation.get("user_id")) 
            for translation in translations.find({
                "timestamp": {"$gte": today_start.isoformat()}
            })
        ))
        
        weekly_active_users = len(set(
            str(translation.get("user_id")) 
            for translation in translations.find({
                "timestamp": {"$gte": week_start.isoformat()}
            })
        ))
        
        monthly_active_users = len(set(
            str(translation.get("user_id")) 
            for translation in translations.find({
                "timestamp": {"$gte": month_start.isoformat()}
            })
        ))
        
        # Popular features
        favorites_used = favorites.count_documents({})
        history_accessed = translations.count_documents({})
        voice_input_used = voice_translations.count_documents({})
        
        # Usage patterns (daily for last 7 days)
        daily_usage = []
        for i in range(7):
            day_start = today_start - timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            count = translations.count_documents({
                "timestamp": {
                    "$gte": day_start.isoformat(),
                    "$lt": day_end.isoformat()
                }
            })
            daily_usage.append({
                "date": day_start.strftime("%Y-%m-%d"),
                "count": count
            })
        daily_usage.reverse()
        
        # User retention
        retention_data = []
        for i in range(4):  # Last 4 weeks
            week_start_date = week_start - timedelta(weeks=i)
            week_end_date = week_start_date + timedelta(weeks=1)
            
            active_users = len(set(
                str(translation.get("user_id")) 
                for translation in translations.find({
                    "timestamp": {
                        "$gte": week_start_date.isoformat(),
                        "$lt": week_end_date.isoformat()
                    }
                })
            ))
            
            retention_data.append({
                "week": week_start_date.strftime("%Y-%m-%d"),
                "active_users": active_users
            })
        retention_data.reverse()
        
        # Create CSV content
        csv_content = f"""Analytics Report,Generated: {now.strftime('%Y-%m-%d %H:%M:%S')}

Translation Volume,
Today,{translations_today}
This Week,{translations_week}
This Month,{translations_month}

User Engagement,
Daily Active Users,{daily_active_users}
Weekly Active Users,{weekly_active_users}
Monthly Active Users,{monthly_active_users}

Popular Features,
Favorites Used,{favorites_used}
History Accessed,{history_accessed}
Voice Input Used,{voice_input_used}

Usage Patterns (Last 7 Days),Date,Translations
"""
        
        # Add daily usage data
        for day in daily_usage:
            csv_content += f"{day['date']},{day['count']}\n"
        
        csv_content += "\nUser Retention (Last 4 Weeks),Week,Active Users\n"
        
        # Add retention data
        for week in retention_data:
            csv_content += f"{week['week']},{week['active_users']}\n"
        
        # Return CSV file
        response = make_response(csv_content)
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=analytics_export_{datetime.now().strftime("%Y-%m-%d")}.csv'
        
        return response
        
    except Exception as e:
        print(f"Analytics export error: {str(e)}")  # For debugging
        return jsonify({"error": f"Analytics export failed: {str(e)}"}), 500

@admin_routes.route("/admin/reports/export", methods=["GET"])
@admin_required
def export_reports():
    # This endpoint can be used to export data in CSV/Excel format
    # For now, returning JSON data that can be processed by frontend
    somalia_tz = pytz.timezone('Africa/Mogadishu')
    now = datetime.now(somalia_tz)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Get all translations for the current month
    monthly_translations = list(translations.find({
        "timestamp": {"$gte": month_start.isoformat()}
    }).sort("timestamp", -1))
    
    
    # Get all users
    all_users = list(users.find({}))
    
    # Process data for export
    export_data = {
        "monthly_translations": len(monthly_translations),
        "total_users": len(all_users),
        "report_generated": now.isoformat(),
        "data_available": True
    }
    
    return jsonify(export_data)

@admin_routes.route("/admin/users/export", methods=["GET"])
@admin_required
def export_users():
    try:
        # Get all users
        all_users = list(users.find({}).sort("created_at", -1))
        
        # Create CSV content
        csv_content = "Name,Email,Role,Created At,Status\n"
        
        for user in all_users:
            name = user.get('full_name', '').replace('"', '""')  # Escape quotes
            email = user.get('email', '').replace('"', '""')
            role = user.get('role', '').replace('"', '""')
            created_at = user.get('created_at', '')
            status = 'Suspended' if user.get('is_suspended', False) else 'Active'
            
            # Format date
            if created_at:
                try:
                    # Handle different date formats
                    if isinstance(created_at, str):
                        date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    else:
                        date_obj = created_at
                    formatted_date = date_obj.strftime('%m/%d/%Y')
                except:
                    formatted_date = ''
            else:
                formatted_date = ''
            
            # Add row to CSV
            csv_content += f'"{name}","{email}","{role}","{formatted_date}","{status}"\n'
        
        # Return CSV file
        response = make_response(csv_content)
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=users_export_{datetime.now().strftime("%Y-%m-%d")}.csv'
        
        return response
        
    except Exception as e:
        print(f"Export error: {str(e)}")  # For debugging
        return jsonify({"error": f"Export failed: {str(e)}"}), 500