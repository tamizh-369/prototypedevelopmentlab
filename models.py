from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timezone
import uuid

db = SQLAlchemy()

class Admin(UserMixin, db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def get_id(self):
        return f"admin_{self.id}"

class Ambulance(db.Model):
    __tablename__ = 'ambulances'
    id = db.Column(db.Integer, primary_key=True)
    vehicle_number = db.Column(db.String(50), unique=True, nullable=False)
    current_lat = db.Column(db.Float, nullable=True)
    current_lng = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(20), default='available') # available, busy
    base_lat = db.Column(db.Float, nullable=True)
    base_lng = db.Column(db.Float, nullable=True)
    drivers = db.relationship('Driver', back_populates='ambulance')
    incidents = db.relationship('Incident', back_populates='ambulance')

class Driver(UserMixin, db.Model):
    __tablename__ = 'drivers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    ambulance_id = db.Column(db.Integer, db.ForeignKey('ambulances.id'), nullable=True)
    ambulance = db.relationship('Ambulance', back_populates='drivers')

    def get_id(self):
        return f"driver_{self.id}"

class Hospital(db.Model):
    __tablename__ = 'hospitals'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    hospital_type = db.Column(db.String(50), nullable=False) # govt, private
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    severity_capabilities = db.Column(db.String(200), nullable=True) # comma separated tags
    available_beds = db.Column(db.Integer, default=0)
    incidents = db.relationship('Incident', back_populates='hospital')

class Incident(db.Model):
    __tablename__ = 'incidents'
    id = db.Column(db.Integer, primary_key=True)
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    severity = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default='reported') 
    # reported, assigned, en_route, reached, hospital_redirect, completed
    reporter_contact = db.Column(db.String(50), nullable=True)
    tracking_token = db.Column(db.String(100), unique=True, default=lambda: str(uuid.uuid4()))
    ambulance_id = db.Column(db.Integer, db.ForeignKey('ambulances.id'), nullable=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    ambulance = db.relationship('Ambulance', back_populates='incidents')
    hospital = db.relationship('Hospital', back_populates='incidents')
