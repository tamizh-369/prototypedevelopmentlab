import time
import math
import os
from app import app, db
from models import Ambulance, Incident

SIM_SPEED_FILE = 'D:/PDL/sim_speed.txt'

def get_speed():
    try:
        with open(SIM_SPEED_FILE, 'r') as f:
            return float(f.read().strip())
    except:
        return 0.0 # 0 means paused

def move_ambulances():
    speed_multiplier = get_speed()
    if speed_multiplier <= 0: 
        return

    with app.app_context():
        busy_ambs = Ambulance.query.filter_by(status='busy').all()
        for amb in busy_ambs:
            inc = Incident.query.filter_by(ambulance_id=amb.id).filter(Incident.status.in_(['assigned', 'en_route'])).first()
            if not inc:
                continue

            lat1, lon1 = amb.current_lat, amb.current_lng
            lat2, lon2 = inc.lat, inc.lng
            
            # Distance logic
            R = 6371.0 # km
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            dist_km = R * c

            # If within 100 meters, snap to target and set reached
            if dist_km < 0.1:
                amb.current_lat = lat2
                amb.current_lng = lon2
                inc.status = 'reached'
                continue
                
            # Base speed: 60 km/h = 1 km/min = 0.016 km/sec
            # Loop runs every 2 seconds -> base dist moved = 0.033 km per loop at 1x speed
            step_dist = 0.033 * speed_multiplier
            
            # Interpolate
            ratio = min(1.0, step_dist / dist_km)
            amb.current_lat = lat1 + (lat2 - lat1) * ratio
            amb.current_lng = lon1 + (lon2 - lon1) * ratio
            
        db.session.commit()

if __name__ == '__main__':
    print("Live Simulation Engine Started.")
    # Initialize speed file to 0 (paused) if it doesn't exist
    if not os.path.exists(SIM_SPEED_FILE):
        with open(SIM_SPEED_FILE, 'w') as f:
            f.write("0")
            
    while True:
        try:
            move_ambulances()
            time.sleep(2)
        except Exception as e:
            print("Error in simulation:", e)
            time.sleep(5)
