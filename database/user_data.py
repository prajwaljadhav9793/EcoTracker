import json
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

APPLIANCE_POWER = {
    "fan": 0.075,
    "light": 0.02,
    "tv": 0.10,
    "iron": 1.00,
    "refrigerator": 0.15,
    "ac": 1.50
}


# ---------------- USER TABLE ----------------
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    age = db.Column(db.Integer)
    mobile = db.Column(db.String(15))
    password = db.Column(db.String(100), nullable=False)

    appliance_profile = db.relationship(
        "ApplianceProfile",
        backref="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User {self.email}>"


# ---------------- APPLIANCE PROFILE ----------------
class ApplianceProfile(db.Model):
    __tablename__ = "appliance_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)

    profile_photo = db.Column(db.String(255))
    average_duration = db.Column(db.Float, default=0)
    appliances_json = db.Column(db.Text, default="[]")
    total_units = db.Column(db.Float, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_appliances_list(self):
        try:
            return json.loads(self.appliances_json or "[]")
        except Exception:
            return []

    def __repr__(self):
        return f"<ApplianceProfile user_id={self.user_id}>"


# ---------------- HELPERS ----------------
def add_user(name, email, age, mobile, password):
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return None

    try:
        age_int = int(age)
    except (TypeError, ValueError):
        age_int = None

    user = User(
        name=name,
        email=email,
        age=age_int,
        mobile=mobile,
        password=password
    )

    db.session.add(user)
    db.session.commit()
    return user


def check_login(email, password):
    return User.query.filter_by(email=email, password=password).first()


def get_profile(user_id):
    return ApplianceProfile.query.filter_by(user_id=user_id).first()


def calculate_total_units(appliance_items):
    total = 0.0

    for item in appliance_items:
        try:
            hours = float(item.get("hours", 0) or 0)
            watts = float(item.get("power_watts", 0) or 0)
        except (TypeError, ValueError):
            hours = 0.0
            watts = 0.0

        total += (hours * watts) / 1000.0

    return round(total, 2)


def save_profile(user_id, appliance_items, average_duration, photo_filename=None):
    profile = ApplianceProfile.query.filter_by(user_id=user_id).first()

    if not profile:
        profile = ApplianceProfile(user_id=user_id)

    if photo_filename:
        profile.profile_photo = photo_filename

    profile.average_duration = float(average_duration or 0)
    profile.appliances_json = json.dumps(appliance_items)
    profile.total_units = calculate_total_units(appliance_items)

    db.session.add(profile)
    db.session.commit()
    return profile
