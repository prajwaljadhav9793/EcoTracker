# modUles/user.py

def validate_name(name):

    if not name:
        return False, "Name cannot be empty"

    if not name.replace(" ", "").isalpha():
        return False, "Name must contain only letters"

    return True, ""


def validate_email(email):

    if "@" not in email or "." not in email:
        return False, "Invalid email"

    return True, ""


def validate_password(password):

    if len(password) < 6:
        return False, "Password too short"

    return True, ""


def create_user(name, email, age, mobile, password):

    user = {
        "name": name,
        "email": email,
        "age": age,
        "mobile": mobile,
        "password": password
    }

    return user