import os
import math
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
import requests

from models import db, Admin, Driver, Ambulance, Hospital, Incident

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///local.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

@login_manager.user_loader
def load_user(user_id):
    if str(user_id).startswith('admin_'):
        return db.session.get(Admin, int(user_id.split('_')[1]))
    elif str(user_id).startswith('driver_'):
        return db.session.get(Driver, int(user_id.split('_')[1]))
    
    # Fallback for old sessions that might just have '1'
    admin = db.session.get(Admin, int(user_id)) if str(user_id).isdigit() else None
    if admin: return admin
    driver = db.session.get(Driver, int(user_id)) if str(user_id).isdigit() else None
    return driver

def haversine(lat1, lon1, lat2, lon2):
    # Simple distance calculation in km
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# --- Public Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/report', methods=['GET'])
def report_page():
    return render_template('report.html')

@app.route('/api/signal', methods=['POST'])
def api_signal():
    data = request.json
    try:
        lat = float(data.get('lat'))
        lng = float(data.get('lng'))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid or missing location"}), 400
        
    severity = data.get('severity', 'general')
    contact = data.get('contact')

    incident = Incident(lat=lat, lng=lng, severity=severity, reporter_contact=contact)
    db.session.add(incident)
    db.session.commit()

    # --- DEMO MAGIC: Auto-reset and randomize based on accident spot ---
    import random
    available_ambulances = Ambulance.query.filter_by(status='available').all()
    
    # If no ambulances are available, force reset one for the sake of the demo
    if not available_ambulances:
        amb = Ambulance.query.first()
        amb.status = 'available'
        db.session.commit()
        available_ambulances = [amb]

    # Generate a dynamic hospital 1-3km away from the SOS spot
    lat_offset = random.choice([1, -1]) * random.uniform(0.01, 0.03)
    lng_offset = random.choice([1, -1]) * random.uniform(0.01, 0.03)
    hosp_lat = lat + lat_offset
    hosp_lng = lng + lng_offset
    
    hosp = Hospital(
        name=f"City Care Hospital {random.randint(100, 999)}", 
        hospital_type="private", 
        lat=hosp_lat, 
        lng=hosp_lng,
        severity_capabilities="trauma,icu,general"
    )
    db.session.add(hosp)
    
    # Teleport our demo ambulance to this new hospital before assigning
    demo_amb = available_ambulances[0]
    demo_amb.current_lat = hosp_lat
    demo_amb.current_lng = hosp_lng
    db.session.commit()
    # ------------------------------------------------------------------

    # Auto-assign logic
    available_ambulances = Ambulance.query.filter_by(status='available').all()
    best_amb = None
    min_dist = float('inf')

    for amb in available_ambulances:
        if amb.current_lat and amb.current_lng:
            dist = haversine(lat, lng, amb.current_lat, amb.current_lng)
            if dist < min_dist:
                min_dist = dist
                best_amb = amb

    if best_amb:
        incident.ambulance_id = best_amb.id
        incident.status = 'assigned'
        best_amb.status = 'busy'
        db.session.commit()

    return jsonify({
        "message": "Incident reported",
        "incident_id": incident.id,
        "tracking_token": incident.tracking_token,
        "assigned_ambulance": incident.ambulance_id
    })

@app.route('/track/<token>')
def track_incident(token):
    incident = Incident.query.filter_by(tracking_token=token).first_or_404()
    return render_template('track.html', incident=incident)

@app.route('/api/incident/<token>', methods=['GET'])
def api_track(token):
    incident = Incident.query.filter_by(tracking_token=token).first_or_404()
    amb = incident.ambulance
    
    driver_name = None
    driver_phone = None
    if amb and amb.drivers:
        driver = amb.drivers[0]
        driver_name = driver.name
        driver_phone = driver.phone
        
    return jsonify({
        "status": incident.status,
        "ambulance": {
            "id": amb.id if amb else None,
            "vehicle_number": amb.vehicle_number if amb else None,
            "lat": amb.current_lat if amb else None,
            "lng": amb.current_lng if amb else None,
            "driver_name": driver_name,
            "driver_phone": driver_phone
        } if amb else None
    })

# --- Admin Routes ---

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password_hash, password):
            login_user(admin)
            demo_param = request.args.get('demo')
            if demo_param:
                return redirect(url_for('admin_dashboard', demo=demo_param))
            return redirect(url_for('admin_dashboard'))
        flash('Invalid credentials')
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not isinstance(current_user, Admin):
        return "Unauthorized", 403
    incidents = Incident.query.order_by(Incident.created_at.desc()).all()
    return render_template('admin_dashboard.html', incidents=incidents)

@app.route('/api/admin/data')
@login_required
def api_admin_data():
    if not isinstance(current_user, Admin):
        return "Unauthorized", 403
    incidents = Incident.query.order_by(Incident.created_at.desc()).all()
    ambulances = Ambulance.query.all()
    
    amb_data = []
    for a in ambulances:
        driver_name = a.drivers[0].name if a.drivers else "Unassigned"
        active_inc = None
        if a.status == 'busy':
            inc = Incident.query.filter_by(ambulance_id=a.id)\
                    .filter(Incident.status.in_(['assigned', 'en_route', 'reached'])).first()
            if inc:
                active_inc = {'lat': inc.lat, 'lng': inc.lng, 'id': inc.id, 'severity': inc.severity}
                
        amb_data.append({
            "id": a.id,
            "vehicle_number": a.vehicle_number,
            "lat": a.current_lat,
            "lng": a.current_lng,
            "status": a.status,
            "driver_name": driver_name,
            "active_incident": active_inc
        })
    
    return jsonify({
        "incidents": [{
            "id": i.id,
            "lat": i.lat,
            "lng": i.lng,
            "status": i.status,
            "severity": i.severity
        } for i in incidents],
        "ambulances": amb_data
    })

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# --- Driver Routes ---

@app.route('/driver/login', methods=['GET', 'POST'])
def driver_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        driver = Driver.query.filter_by(username=username).first()
        if driver and check_password_hash(driver.password_hash, password):
            login_user(driver)
            demo_param = request.args.get('demo')
            if demo_param:
                return redirect(url_for('driver_dashboard', demo=demo_param))
            return redirect(url_for('driver_dashboard'))
        flash('Invalid credentials')
    return render_template('driver_login.html')

@app.route('/driver/dashboard')
@login_required
def driver_dashboard():
    if not isinstance(current_user, Driver):
        return "Unauthorized", 403
    
    # Get active incident for this driver's ambulance
    incident = Incident.query.filter_by(ambulance_id=current_user.ambulance_id)\
                    .filter(Incident.status.in_(['assigned', 'en_route', 'reached'])).first()
                    
    return render_template('driver_dashboard.html', incident=incident)

@app.route('/api/driver/location', methods=['POST'])
@login_required
def api_driver_location():
    if not isinstance(current_user, Driver):
        return "Unauthorized", 403
    data = request.json
    amb = current_user.ambulance
    if amb:
        amb.current_lat = data.get('lat')
        amb.current_lng = data.get('lng')
        db.session.commit()
    return jsonify({"status": "updated"})

@app.route('/api/driver/status', methods=['POST'])
@login_required
def api_driver_status():
    if not isinstance(current_user, Driver):
        return "Unauthorized", 403
    
    data = request.json
    new_status = data.get('status')
    
    incident = Incident.query.filter_by(ambulance_id=current_user.ambulance_id)\
                    .filter(Incident.status.in_(['assigned', 'en_route', 'reached'])).first()
    
    if incident:
        incident.status = new_status
        # If reached, find nearest hospital and assign
        if new_status == 'reached':
            hospitals = Hospital.query.all()
            best_hosp = None
            min_dist = float('inf')
            for h in hospitals:
                dist = haversine(incident.lat, incident.lng, h.lat, h.lng)
                if dist < min_dist:
                    min_dist = dist
                    best_hosp = h
            if best_hosp:
                incident.hospital_id = best_hosp.id
                
        elif new_status == 'completed':
            current_user.ambulance.status = 'available'
            
        db.session.commit()
        
    return jsonify({"status": "updated"})

# --- Init db script ---
def init_db():
    with app.app_context():
        db.create_all()
        # Seed admin
        if not Admin.query.first():
            admin = Admin(username='admin', password_hash=generate_password_hash('admin'))
            db.session.add(admin)
        
        # Seed hospital
        if not Hospital.query.first():
            hosp = Hospital(name='City Central Hospital', hospital_type='govt', lat=13.0827, lng=80.2707, severity_capabilities='trauma,icu')
            db.session.add(hosp)
            
        # Seed ambulance & driver
        if not Ambulance.query.first():
            amb = Ambulance(vehicle_number='TN-01-AB-1234', current_lat=13.0800, current_lng=80.2700, status='available')
            db.session.add(amb)
            db.session.commit()
            
            driver = Driver(name='John Driver', phone='9999999999', username='driver1', password_hash=generate_password_hash('driver'), ambulance_id=amb.id)
            db.session.add(driver)
            
        db.session.commit()

@app.route('/api/admin/sim_speed', methods=['POST'])
@login_required
def set_sim_speed():
    if not isinstance(current_user, Admin):
        return "Unauthorized", 403
    speed = request.json.get('speed', 0)
    with open('D:/PDL/sim_speed.txt', 'w') as f:
        f.write(str(speed))
    return jsonify({"status": "ok"})
    
@app.route('/api/admin/sim_speed', methods=['GET'])
@login_required
def get_sim_speed():
    if not isinstance(current_user, Admin):
        return "Unauthorized", 403
    try:
        with open('D:/PDL/sim_speed.txt', 'r') as f:
            speed = float(f.read().strip())
    except:
        speed = 0.0
    return jsonify({"speed": speed})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
