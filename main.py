import sys
import os
import json
from uuid import uuid4

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, url_for, redirect, session, flash
from werkzeug.utils import secure_filename

from modules.user import (
    validate_name,
    validate_email,
    validate_password
)

from database.user_data import (
    db,
    User,
    add_user,
    check_login,
    get_profile,
    save_profile
)

from modules.emissions import calculate_emissions
from modules.calculator import calculate_score
from modules.ai_module import get_ai_suggestions
from modules.gamification import leaderboard, update_leaderboard

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database', 'user_database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

db.init_app(app)

app.secret_key = "secret123"

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

DEFAULT_APPLIANCES = [
    {"key": "fan", "name": "Fan", "category": "Cooling", "watts": 75},
    {"key": "light", "name": "Light", "category": "Lighting", "watts": 20},
    {"key": "tv", "name": "TV", "category": "Entertainment", "watts": 100},
    {"key": "iron", "name": "Iron", "category": "Heating", "watts": 1000},
    {"key": "refrigerator", "name": "Refrigerator", "category": "Cooling", "watts": 150},
    {"key": "ac", "name": "AC", "category": "Cooling", "watts": 1500},
]


def allowed_photo(filename):
    if not filename:
        return False
    ext = os.path.splitext(filename)[1].lower()
    return ext in {'.png', '.jpg', '.jpeg', '.webp'}


def save_photo(photo_file, user_id):
    if not photo_file or not photo_file.filename:
        return None

    if not allowed_photo(photo_file.filename):
        return None

    original = secure_filename(photo_file.filename)
    ext = os.path.splitext(original)[1].lower()
    filename = f"user_{user_id}_{uuid4().hex}{ext}"
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    photo_file.save(save_path)
    return filename


def build_appliance_items(form):
    names = form.getlist("appliance_name[]")
    types = form.getlist("appliance_type[]")
    hours = form.getlist("usage_hours[]")
    watts = form.getlist("power_watts[]")

    items = []
    for name, typ, hour, watt in zip(names, types, hours, watts):
        name = (name or "").strip()
        typ = (typ or "General").strip()

        if not name:
            continue

        try:
            hour_f = float(hour)
        except (TypeError, ValueError):
            hour_f = 0.0

        try:
            watt_f = float(watt)
        except (TypeError, ValueError):
            watt_f = 0.0

        units = round((hour_f * watt_f) / 1000.0, 2)

        items.append({
            "name": name,
            "type": typ,
            "hours": hour_f,
            "power_watts": watt_f,
            "units": units
        })

    return items

@app.route('/')
def home():
    navbar_photo = None

    if session.get('user_id'):
        user = db.session.get(User, session['user_id'])
        if user and user.appliance_profile and user.appliance_profile.profile_photo:
            navbar_photo = url_for('static', filename=f'uploads/{user.appliance_profile.profile_photo}')

    return render_template("home.html", navbar_photo=navbar_photo)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = check_login(email, password)

        if user:
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['user'] = user.email
            return redirect('/calculator')

        return render_template('login.html', error='Invalid Email or Password')

    return render_template("login.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        age = request.form['age']
        mobile = request.form['mobile']
        password = request.form['password']

        valid, msg = validate_name(name)
        if not valid:
            return render_template("register.html", error=msg)

        valid, msg = validate_email(email)
        if not valid:
            return render_template("register.html", error=msg)

        valid, msg = validate_password(password)
        if not valid:
            return render_template("register.html", error=msg)

        new_user = add_user(name, email, age, mobile, password)

        if not new_user:
            return render_template("register.html", error="Email already exists")

        session['user_id'] = new_user.id
        session['user_email'] = new_user.email
        session['user'] = new_user.email

        flash("Registration successful. Now create your profile.")
        return redirect(url_for('create_profile'))

    return render_template("register.html")


@app.route('/profile/create', methods=['GET', 'POST'])
def create_profile():
    if 'user_id' not in session:
        return redirect('/login')

    user = db.session.get(User, session['user_id'])
    if not user:
        return redirect('/login')

    if get_profile(user.id):
        return redirect(url_for('profile'))

    if request.method == 'POST':
        appliances = build_appliance_items(request.form)

        if not appliances:
            flash("Please select or add at least one appliance.")
            return render_template(
                "create_profile.html",
                user=user,
                default_appliances=DEFAULT_APPLIANCES
            )

        photo_file = request.files.get('profile_photo')
        photo_filename = save_photo(photo_file, user.id)

        if photo_file and photo_file.filename and not photo_filename:
            flash("Only PNG, JPG, JPEG, or WEBP images are allowed.")
            return render_template(
                "create_profile.html",
                user=user,
                default_appliances=DEFAULT_APPLIANCES
            )

        average_duration = request.form.get('average_duration', 0)
        save_profile(user.id, appliances, average_duration, photo_filename)

        flash("Registration and profile creation successful.")
        return redirect(url_for('profile'))

    return render_template(
        "create_profile.html",
        user=user,
        default_appliances=DEFAULT_APPLIANCES
    )


@app.route('/profile', methods=['GET'])
def profile():
    if 'user_id' not in session:
        return redirect('/login')

    user = db.session.get(User, session['user_id'])
    if not user:
        return redirect('/login')

    profile_data = get_profile(user.id)
    if not profile_data:
        return redirect(url_for('create_profile'))

    appliances = profile_data.get_appliances_list()
    photo_url = None

    if profile_data.profile_photo:
        photo_url = url_for('static', filename=f'uploads/{profile_data.profile_photo}')

    return render_template(
        "profile.html",
        user=user,
        profile=profile_data,
        appliances=appliances,
        photo_url=photo_url,
        default_appliances=DEFAULT_APPLIANCES
    )


@app.route('/profile/update', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return redirect('/login')

    user = db.session.get(User, session['user_id'])
    if not user:
        return redirect('/login')

    appliances = build_appliance_items(request.form)

    if not appliances:
        flash("Please select or add at least one appliance.")
        return redirect(url_for('profile'))

    photo_file = request.files.get('profile_photo')
    photo_filename = save_photo(photo_file, user.id)

    if photo_file and photo_file.filename and not photo_filename:
        flash("Only PNG, JPG, JPEG, or WEBP images are allowed.")
        return redirect(url_for('profile'))

    average_duration = request.form.get('average_duration', 0)
    save_profile(user.id, appliances, average_duration, photo_filename)

    flash("Profile updated successfully.")
    return redirect(url_for('profile'))


@app.route("/calculator", methods=['GET', 'POST'])
def calculator():

    # ================= SESSION CHECK =================

    if 'user_id' not in session and 'guest_email' not in session:

        email = request.args.get('email')

        if email:

            session['guest_email'] = email
            session['user'] = email

        else:

            return redirect('/login')

    # ================= GET REQUEST =================

    if request.method == 'GET':

        distance = request.args.get('distance', '')

        vehicle = request.args.get('vehicle', 'Car')

        # Detect Quick Start mode
        quick_mode = request.args.get('quick', 'false')

        # Default empty values
        electricity = ""
        waste = ""

        # ONLY autofill in Quick Start mode
        if quick_mode == 'true':

            if session.get('user_id'):

                profile_data = get_profile(session['user_id'])

                if profile_data:

                    # Get total electricity units
                    electricity = profile_data.total_units

                    # Get appliance list
                    appliances = profile_data.get_appliances_list()

                    if appliances:

                        # Calculate waste estimate from appliance usage
                        total_hours = 0

                        for appliance in appliances:

                            total_hours += appliance.get("hours", 0)

                        waste = round(total_hours * 0.08, 1)

        return render_template(

            "calculator.html",

            distance=distance,

            electricity=electricity,

            waste=waste,

            selected_vehicle=vehicle,

            vehicle=vehicle
        )

    # ================= POST REQUEST =================

    distance = float(request.form.get('distance', 0))

    electricity = float(request.form.get('electricity', 0))

    vehicle = request.form.get('vehicle', 'Car')

    waste = float(request.form.get('waste', 0))

    breakdown, total_co2, highest_source = calculate_emissions(

        electricity,
        vehicle,
        distance,
        waste,
        0,
        0
    )

    total_score, message, values = calculate_score(

        vehicle,
        electricity,
        waste
    )

    user_label = (

        session.get('user_email')

        or session.get('guest_email')

        or session.get('user')

        or 'Guest'
    )

    update_leaderboard(user_label, total_score)

    user_data = {

        "carbon": total_co2,

        "highest_source": highest_source,

        "transport_co2": breakdown["Transport"],

        "electricity_co2": breakdown["Electricity"],

        "waste_co2": breakdown["Waste"],

        "gas_co2": breakdown["Gas"],

        "appliance_co2": breakdown["Appliances"]
    }

    if total_co2 < 5:

        tips = [
            "Great job. Your carbon footprint is already low."
        ]

    else:

        tips = get_ai_suggestions(user_data)

    return render_template(

        "result.html",

        carbon=total_co2,

        total=total_score,

        message=message,

        labels=['Transport', 'Electricity', 'Waste'],

        values=values,

        breakdown=breakdown,

        tips=tips
    )
# ---------------- QUICK START ----------------
@app.route('/quickstart')
def quickstart():

    if 'user_id' not in session:

        flash("Please login first.")

        return redirect('/login')

    return render_template("quickstart.html")

@app.route('/map')
def map():
    return render_template('map.html')


@app.route('/result')
def result():
    distance = float(request.args.get('distance', 0))
    vehicle = request.args.get('vehicle', 'Car')

    breakdown, total_co2, highest_source = calculate_emissions(
        0,
        vehicle,
        distance,
        0,
        0,
        0
    )

    user_data = {
        "carbon": total_co2,
        "highest_source": highest_source,
        "transport_co2": breakdown["Transport"],
        "electricity_co2": breakdown["Electricity"],
        "waste_co2": breakdown["Waste"],
        "gas_co2": breakdown["Gas"],
        "appliance_co2": breakdown["Appliances"]
    }

    if total_co2 < 5:
        tips = ["Great job. Your carbon footprint is already low."]
    else:
        tips = get_ai_suggestions(user_data)

    return render_template(
        "result.html",
        carbon=total_co2,
        total=5,
        message="Journey Result 🚀",
        labels=['Transport', 'Electricity', 'Waste'],
        values=[5, 0, 0],
        breakdown=breakdown,
        tips=tips
    )


@app.route('/leaderboard')
def show_leaderboard():
    return render_template("leaderboard.html", leaderboard=leaderboard)


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_email', None)
    session.pop('guest_email', None)
    session.pop('user', None)
    return redirect('/login')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)

