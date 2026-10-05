from app import app, db
from models import Ambulance, Driver
from werkzeug.security import generate_password_hash

def seed_more():
    with app.app_context():
        # Check how many we have
        count = Ambulance.query.count()
        if count < 3:
            ambs = [
                {'v': 'TN-02-CD-5678', 'lat': 13.0600, 'lng': 80.2400, 'd_user': 'driver2', 'd_name': 'Sarah Smith'},
                {'v': 'TN-03-EF-9012', 'lat': 13.1000, 'lng': 80.2200, 'd_user': 'driver3', 'd_name': 'Mike Johnson'}
            ]
            for a in ambs:
                amb = Ambulance(vehicle_number=a['v'], current_lat=a['lat'], current_lng=a['lng'], status='available')
                db.session.add(amb)
                db.session.flush()
                driver = Driver(name=a['d_name'], phone='9999999999', username=a['d_user'], password_hash=generate_password_hash('driver'), ambulance_id=amb.id)
                db.session.add(driver)
            db.session.commit()
            print("Seeded additional drivers successfully.")
        else:
            print("Drivers already exist.")

if __name__ == "__main__":
    seed_more()
