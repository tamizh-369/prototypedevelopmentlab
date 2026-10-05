import time
from datetime import datetime, timezone, timedelta
from app import app, db
from models import Incident, Ambulance

def cleanup_old_reports():
    with app.app_context():
        # 1 hour ago
        threshold = datetime.now(timezone.utc) - timedelta(hours=1)
        
        # We need to gracefully handle naive vs aware datetimes based on the DB driver
        try:
            old_incidents = Incident.query.filter(Incident.created_at < threshold).all()
        except Exception:
            # Fallback to naive datetime if the DB driver complains about timezone-aware comparison
            threshold_naive = datetime.utcnow() - timedelta(hours=1)
            old_incidents = Incident.query.filter(Incident.created_at < threshold_naive).all()
        
        if not old_incidents:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] No incidents older than 1 hour found.")
            return

        for inc in old_incidents:
            # If an ambulance was assigned to this old incident, mark it available again
            if inc.ambulance_id:
                amb = Ambulance.query.get(inc.ambulance_id)
                # Ensure we only reset if it's currently busy
                if amb and amb.status == 'busy':
                    amb.status = 'available'
            
            db.session.delete(inc)
            
        db.session.commit()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Automatically cleared {len(old_incidents)} old incident(s).")

if __name__ == "__main__":
    print("Starting background cleanup worker...")
    print("This will check for and delete reports older than 1 hour, freeing up their ambulances.")
    while True:
        try:
            cleanup_old_reports()
            # Wait 10 minutes before checking again
            time.sleep(600)
        except KeyboardInterrupt:
            print("Stopping cleanup worker.")
            break
        except Exception as e:
            print(f"Error during cleanup: {e}")
            time.sleep(60)
