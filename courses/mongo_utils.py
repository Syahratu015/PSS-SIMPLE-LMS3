from pymongo import MongoClient
from datetime import datetime


client = MongoClient("mongodb://mongodb:27017/")
db = client["simple_lms"]

activity_logs = db["activity_logs"]
learning_analytics = db["learning_analytics"]


def log_activity(user_id, action, detail):
    activity_logs.insert_one({
        "user_id": user_id,
        "action": action,
        "detail": detail,
        "created_at": datetime.utcnow()
    })


def log_learning_analytics(user_id, course_id, event_type, progress=0):
    learning_analytics.insert_one({
        "user_id": user_id,
        "course_id": course_id,
        "event_type": event_type,
        "progress": progress,
        "created_at": datetime.utcnow()
    })