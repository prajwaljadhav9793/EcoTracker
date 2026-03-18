import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request
from modules.user import (
    validate_name,
    validate_email,
    validate_password,
    create_user
)

app = Flask(__name__)


# Home page
@app.route('/')
def home():
    return render_template("home.html")

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        #print("Login:", email, password)

        return "Login Successful"

    return render_template("login.html")


# Register page
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        age = request.form['age']
        mobile = request.form['mobile']
        password = request.form['password']

        # validation
        valid, msg = validate_name(name)
        if not valid:
            return msg

        valid, msg = validate_email(email)
        if not valid:
            return msg

        valid, msg = validate_password(password)
        if not valid:
            return msg

        user = create_user(name, email, age, mobile, password)

        print("User created:", user)

        return "Registration Successful"

    return render_template("register.html")


# Calculator result
@app.route("/calculator", methods=['GET','POST'])
def calculator():
    return render_template("calculator.html")

# Dashboard page
@app.route('/dashboard', methods=['GET','POST'])
def dashboard():
    return render_template("dashboard.html")

@app.route('/result', methods=['GET','POST'])
def result():
    return render_template("result.html")


if __name__ == '__main__':
    app.run(debug=True)
