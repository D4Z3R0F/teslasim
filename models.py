import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="driver")
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    simulations = db.relationship("Simulation", backref="user", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Simulation(db.Model):
    __tablename__ = "simulations"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(100), default="My Roadster")
    battery_percent = db.Column(db.Float, default=100.0)
    speed_kmh = db.Column(db.Float, default=0.0)
    odometer_km = db.Column(db.Float, default=0.0)
    drive_mode = db.Column(db.String(10), default="normal")
    autopilot = db.Column(db.Boolean, default=False)
    climate_temp = db.Column(db.Float, default=21.0)
    is_running = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class Trip(db.Model):
    __tablename__ = "trips"
    id = db.Column(db.Integer, primary_key=True)
    simulation_id = db.Column(db.Integer, db.ForeignKey("simulations.id"), nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    ended_at = db.Column(db.DateTime)
    distance_km = db.Column(db.Float, default=0.0)
    max_speed = db.Column(db.Float, default=0.0)
    energy_used_kwh = db.Column(db.Float, default=0.0)


class Alert(db.Model):
    __tablename__ = "alerts"
    id = db.Column(db.Integer, primary_key=True)
    simulation_id = db.Column(db.Integer, db.ForeignKey("simulations.id"), nullable=False)
    severity = db.Column(db.String(10), default="info")
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class TelemetryEvent(db.Model):
    __tablename__ = "telemetry_events"
    id = db.Column(db.Integer, primary_key=True)
    simulation_id = db.Column(db.Integer, db.ForeignKey("simulations.id"), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)
    payload = db.Column(db.Text)  # храним JSON в виде текста
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class UserSetting(db.Model):
    __tablename__ = "user_settings"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    units = db.Column(db.String(10), default="metric")
    theme = db.Column(db.String(10), default="dark")