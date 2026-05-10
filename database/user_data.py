from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# ---------------- USER TABLE ----------------
class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False)
    age = db.Column(db.Integer)
    mobile = db.Column(db.String(15))
    password = db.Column(db.String(100), nullable=False)


    def __repr__(self):
        return f"<User {self.email}>"
    
# ---------------- ADD USER ----------------
def add_user(name, email, age, mobile, password):

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return False

    new_user = User(
        name=name,
        email=email,
        age=age,
        mobile=mobile,
        password=password
    )

    db.session.add(new_user)
    db.session.commit()

    return True


# ---------------- CHECK LOGIN ----------------
def check_login(email, password):

    user = User.query.filter_by(email=email, password=password).first()

    if user:
        return True

    return False

