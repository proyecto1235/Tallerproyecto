"""
MongoDB Seed Script for RoboLearn Behavioral Tracking
Poblates behavioral_events, frustration_signals, engagement_scores con datos históricos realistas
Ejecutar: python backend/scripts/seed_mongodb.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime, timedelta, timezone
import random
import math
from pymongo import MongoClient
from config.settings import settings

random.seed(42)

def seed_mongodb():
    client = MongoClient(settings.mongodb_url, serverSelectionTimeoutMS=5000)
    db = client[settings.mongodb_db]
    
    # Get real student IDs from PostgreSQL
    import psycopg2
    conn = psycopg2.connect(
        host=settings.postgres_host, port=settings.postgres_port,
        dbname=settings.postgres_db, user=settings.postgres_user,
        password=settings.postgres_password
    )
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE role = 'student' ORDER BY id")
    student_ids = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT id, module_id FROM exercises ORDER BY id")
    exercises = cur.fetchall()
    cur.close()
    conn.close()
    
    print(f"Found {len(student_ids)} students, {len(exercises)} exercises")
    
    # Clear existing data
    for col in ['behavioral_events', 'frustration_signals', 'engagement_scores',
                'session_metrics', 'code_analysis', 'exercise_attempts',
                'weekly_student_metrics', 'ml_predictions']:
        db[col].delete_many({})
        print(f"Cleared {col}")
    
    # 1. Generate behavioral_events (last 30 days)
    now = datetime.now(timezone.utc)
    behavioral_batch = []
    actions = ['view_content', 'start_exercise', 'submit_code', 'view_hint', 'complete_exercise']
    weights = [0.30, 0.25, 0.25, 0.10, 0.10]
    
    for sid in student_ids[:500]:  # 500 students for manageable seed
        n_events = random.randint(5, 40)
        for _ in range(n_events):
            days_ago = random.uniform(0, 30)
            ts = now - timedelta(days=days_ago)
            action = random.choices(actions, weights=weights)[0]
            ex = random.choice(exercises) if exercises else (0, 0)
            behavioral_batch.append({
                "user_id": sid,
                "exercise_id": ex[0],
                "module_id": ex[1],
                "action": action,
                "metadata": {"score": round(random.uniform(0, 100), 1)},
                "timestamp": ts,
            })
        if len(behavioral_batch) >= 500:
            db.behavioral_events.insert_many(behavioral_batch)
            behavioral_batch = []
    
    if behavioral_batch:
        db.behavioral_events.insert_many(behavioral_batch)
    print(f"Seeded behavioral_events")
    
    # 2. Generate frustration_signals (about 15% of students)
    fr_batch = []
    signals = ['compile_error', 'repeated_failure', 'hint_requested', 'execution_error']
    fr_weights = [0.35, 0.25, 0.30, 0.10]
    
    frustrated_students = random.sample(student_ids[:500], min(75, len(student_ids[:500])))
    for sid in frustrated_students:
        n_signals = random.randint(1, 8)
        for _ in range(n_signals):
            days_ago = random.uniform(0, 30)
            ts = now - timedelta(days=days_ago)
            sig_type = random.choices(signals, weights=fr_weights)[0]
            fr_batch.append({
                "user_id": sid,
                "exercise_id": random.choice(exercises)[0] if exercises else 0,
                "signal_type": sig_type,
                "details": f"{sig_type} at week {random.randint(1, 4)}",
                "timestamp": ts,
            })
    
    if fr_batch:
        db.frustration_signals.insert_many(fr_batch)
    print(f"Seeded frustration_signals")
    
    # 3. Generate engagement_scores
    eng_batch = []
    for sid in student_ids[:500]:
        events_count = random.randint(3, 50)
        total_time = random.uniform(30, 600)
        session_days = random.randint(1, 14)
        fr_count = random.randint(0, 5)
        eng = max(0.0, min(1.0,
            0.3 * min(1.0, events_count / 50) +
            0.3 * min(1.0, total_time / 10800) +
            0.3 * min(1.0, session_days / 7) -
            min(0.5, fr_count * 0.05)))
        eng_batch.append({
            "user_id": sid,
            "module_id": None,
            "engagement_score": round(eng, 4),
            "events_count": events_count,
            "total_time_minutes": round(total_time, 2),
            "session_days": session_days,
            "frustration_count": fr_count,
            "calculated_at": now,
        })
    
    if eng_batch:
        db.engagement_scores.insert_many(eng_batch)
    print(f"Seeded engagement_scores")
    
    # 4. Generate session_metrics
    sess_batch = []
    for sid in student_ids[:300]:
        n_sessions = random.randint(2, 15)
        for _ in range(n_sessions):
            days_ago = random.uniform(0, 30)
            start = now - timedelta(days=days_ago)
            duration = random.uniform(120, 7200)
            sess_batch.append({
                "user_id": sid,
                "session_id": f"seed_{sid}_{start.timestamp()}",
                "duration_seconds": duration,
                "events_count": random.randint(1, 30),
                "date": start,
            })
    
    if sess_batch:
        db.session_metrics.insert_many(sess_batch)
    print(f"Seeded session_metrics")
    
    # 5. Generate code_analysis
    code_batch = []
    for sid in student_ids[:200]:
        n_entries = random.randint(1, 10)
        for _ in range(n_entries):
            has_error = random.random() < 0.4
            days_ago = random.uniform(0, 30)
            code_batch.append({
                "user_id": sid,
                "exercise_id": random.choice(exercises)[0] if exercises else 0,
                "code_length": random.randint(10, 500),
                "has_error": has_error,
                "error": "SyntaxError: invalid syntax" if has_error else "",
                "error_type": "SyntaxError" if has_error else "",
                "timestamp": now - timedelta(days=days_ago),
            })
    
    if code_batch:
        db.code_analysis.insert_many(code_batch)
    print(f"Seeded code_analysis")
    
    # 6. Generate weekly_student_metrics (last 4 weeks)
    weekly_batch = []
    for sid in student_ids[:500]:
        for week_offset in range(4):
            week_start = now - timedelta(weeks=week_offset + 1, days=now.weekday())  # Monday
            week_end = week_start + timedelta(days=7)
            weekly_batch.append({
                "user_id": sid,
                "week_start": week_start,
                "week_end": week_end,
                "session_days": random.randint(1, 7),
                "total_sessions": random.randint(2, 20),
                "total_time_minutes": round(random.uniform(30, 600), 2),
                "exercises_attempted": random.randint(1, 15),
                "exercises_passed": random.randint(0, 12),
                "average_score": round(random.uniform(0.3, 1.0), 4),
                "engagement_score": round(random.uniform(0.3, 1.0), 4),
                "created_at": now,
            })
    
    if weekly_batch:
        db.weekly_student_metrics.insert_many(weekly_batch)
    print(f"Seeded weekly_student_metrics")
    
    # Stats
    print(f"\nSeed complete!")
    for col in ['behavioral_events', 'frustration_signals', 'engagement_scores',
                'session_metrics', 'code_analysis', 'weekly_student_metrics']:
        count = db[col].count_documents({})
        print(f"  {col}: {count} documents")
    
    client.close()

if __name__ == "__main__":
    seed_mongodb()
