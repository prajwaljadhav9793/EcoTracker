import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
   
from flask import Flask, render_template, request, redirect, session

from modules.user import (
    validate_name,
    validate_email,
    validate_password
)

from database.user_data import (
    db,
    add_user,
    check_login
)

from modules.emissions import calculate_emissions
from modules.calculator import calculate_score
from modules.ai_module import get_ai_suggestions
from modules.gamification import leaderboard, update_leaderboard

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database', 'user_database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)
app.secret_key = "secret123"



# ------------------ HOME ------------------
@app.route('/')
def home():
    return render_template("home.html")


# ------------------ LOGIN ------------------
# ------------------ LOGIN ------------------
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        valid_user = check_login(email, password)

        if valid_user:
            session['user'] = email
            return redirect('/calculator')

        return render_template(
            'login.html',
            error='Invalid Email or Password'
        )

    return render_template("login.html")


# ------------------ REGISTER ------------------
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

        success = add_user(name, email, age, mobile, password)

        if not success:
            return render_template("register.html", error="Email already exists")

        return redirect("/login")

    return render_template("register.html")


# ------------------ CALCULATOR ------------------
@app.route("/calculator", methods=['GET', 'POST'])
def calculator():

    # ✅ Handle session properly
    if 'user' not in session:
        email = request.args.get('email')

        if email:
            session['user'] = email
        else:
            return redirect('/login')

    # ✅ GET request (from map or direct open)
    if request.method == 'GET':
        distance = request.args.get('distance', 0)
        vehicle = request.args.get('vehicle', 'Car')

        return render_template(
            "calculator.html",
            distance=distance,
            selected_vehicle=vehicle
        )

    # ✅ POST request (form submission)
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

    total_score, message, values = calculate_score(vehicle, electricity, waste)

    update_leaderboard(session['user'], total_score)

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
        total=total_score,
        message=message,
        labels=['Transport', 'Electricity', 'Waste'],
        values=values,
        breakdown=breakdown,
        tips=tips
    )


# ------------------ MAP ------------------
@app.route('/map')
def map():
    return render_template('map.html')


# ------------------ RESULT FROM MAP ------------------
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

    # ✅ FIXED AI DATA
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

# ------------------ LEADERBOARD ------------------
@app.route('/leaderboard')
def show_leaderboard():
    return render_template("leaderboard.html", leaderboard=leaderboard)

# ------------------ LOGOUT ------------------
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')


# ------------------ RUN ------------------
if __name__ == '__main__':

    with app.app_context():
        db.create_all()

    app.run(debug=True)
