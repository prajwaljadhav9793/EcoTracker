import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, redirect, session
from modules.user import (
    validate_name,
    validate_email,
    validate_password,
    create_user
)

app = Flask(__name__)
app.secret_key = "secret123"

# TEMP STORAGE
users = {}


# ------------------ HOME ------------------
@app.route('/')
def home():
    return render_template("home.html")


# ------------------ LOGIN ------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if email in users and users[email] == password:
            session['user'] = email
            return redirect('/calculator')
        else:
            return render_template("login.html", error="Invalid credentials")

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

        if email in users:
            return render_template("register.html", error="Email already exists")

        users[email] = password

        create_user(name, email, age, mobile, password)

        return redirect("/login")

    return render_template("register.html")


# ------------------ CALCULATOR ------------------
@app.route("/calculator", methods=['GET', 'POST'])
def calculator():

    email = request.args.get('email')

    if 'user' not in session:
        if email:
            session['user'] = email
        else:
            return redirect('/login')

    if request.method == 'GET':
        return render_template("calculator.html", distance=0)

    
    labels = ['Transport', 'Electricity', 'Waste']

    distance = float(request.form['distance'])
    electricity = float(request.form['electricity'])
    vehicle = request.form['vehicle']
    waste = float(request.form['waste'])

    vehicle_factor = {
        "Car": 0.21,
        "Bike": 0.12,
        "Bus": 0.10,
        "electric car": 0.05,
        "electric bike": 0.02,
        "Bicycle": 0.01,
        "Walk": 0.0
    }

    transport_co2 = round(distance * vehicle_factor.get(vehicle, 0.21), 2)
    electricity_co2 = round(electricity * 0.82, 2)
    waste_co2 = round(waste * 0.8, 2)
    total_co2 = round(transport_co2 + electricity_co2 + waste_co2, 2)

    vehicle_score_map = {
        "Car": 5,
        "Bike": 7,
        "Bus": 8,
        "electric car": 9,
        "electric bike": 10,
        "Bicycle": 10,
        "Walk": 10
    }

    vehicle_score = vehicle_score_map.get(vehicle, 5)

    electricity_score = 10 if electricity <= 50 else 7 if electricity <= 100 else 4
    waste_score = 10 if waste <= 2 else 6 if waste <= 5 else 3

    values = [vehicle_score, electricity_score, waste_score]
    total_score = sum(values)

    breakdown = {
        "Transport": transport_co2,
        "Electricity": electricity_co2,
        "Waste": waste_co2
    }

    if total_score >= 25:
        message = "Excellent 🌱 Eco Friendly!"
    elif total_score >= 15:
        message = "Good 👍 Keep Improving!"
    else:
        message = "Needs Improvement ⚠️"

    return render_template(
        "result.html",
        carbon=total_co2,
        total=total_score,
        message=message,
        labels=labels,
        values=values,
        breakdown=breakdown
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

    vehicle_factor = {
        "Car": 0.21,
        "Bike": 0.12,
        "Bus": 0.10,
        "electric car": 0.05,
        "electric bike": 0.02,
        "Bicycle": 0.01,
        "Walk": 0.0
    }

    transport_co2 = round(distance * vehicle_factor.get(vehicle, 0.21), 2)

    labels = ['Transport', 'Electricity', 'Waste']

    values = [5, 0, 0]

    breakdown = {
        "Transport": transport_co2,
        "Electricity": 0,
        "Waste": 0
    }

    return render_template(
        "result.html",
        carbon=transport_co2,
        total=5,
        message="Journey Result 🚀",
        labels=labels,
        values=values,
        breakdown=breakdown
    )


# ------------------ LOGOUT ------------------
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')


# ------------------ RUN ------------------
if __name__ == '__main__':
    app.run(debug=True)