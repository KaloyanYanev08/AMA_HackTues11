from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from uuid import uuid4 as genuuid
import re as regex
import hashlib
import requests
from forms import LoginForm

app = Flask(__name__)
app.secret_key = "TESTING_TESTING_123"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    uuid = db.Column(db.String, primary_key=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)

class Activities(db.Model):
    __tablename__ = 'activities'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_uuid = db.Column(db.String, db.ForeignKey('users.uuid'), nullable=False)
    activity_details = db.Column(db.String, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    day_of_week = db.Column(db.String, nullable=False)

class MonthGoals(db.Model):
    __tablename__ = 'month_goals'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_uuid = db.Column(db.String, db.ForeignKey('users.uuid'), nullable=False)
    goal_details = db.Column(db.String, nullable=False)
    hour_goal = db.Column(db.Integer, nullable=True)
    month = db.Column(db.String, nullable=False)

with app.app_context():
    db.create_all()

#region Decorators

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not loggedIn():
            return redirect(url_for('log_in'))
        return f(*args, **kwargs)
    return decorated_function

#endregion

#region Helpers

def toHash(password):
    hash_object = hashlib.sha256()
    hash_object.update(password.encode())
    return hash_object.hexdigest()

def userId():
    try:
        return session["id"]
    except:
        return None

def averageList(list, decimals=-1):
    result = 0
    for item in list:
        result += item
    return (result / len(list)) if decimals == -1 else round(result / len(list), decimals)

def loggedIn():
    try:
        return "id" in session and User.query.filter_by(uuid=str(userId())).first() is not None
    except:
        return False

def isEmptyOrWhitespace(str):
    return str == None or str == "" or str.isspace()

def hasNumber(password):
    return bool(regex.search(r"\d", password))

def hasSpecial(password):
    return bool(regex.search(r"[!@#$%^&*(),.?\":{}|<>]", password))

#endregion

#region User Mgmt

@app.route("/register/", methods=["GET", "POST"])
def register():
    if not request.method == "POST":
        return render_template("register.html", page="Register")

    try:
        username = request.form.get('username')
        password = request.form.get('password')
    except:
        return f"""Fields not filled"""
    
    if len(password) < 8 or not hasNumber(password) or not hasSpecial(password):
        return f"""Pasword be at least 8 characters and have at least one number and special character"""
    
    password = toHash(password)

    if User.query.filter_by(username=username).first() is not None:
        return f"""User exists"""
    
    user_id = str(genuuid())

    new_user = User(uuid=user_id, username=username, password=password)
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('log_in'))

@app.route("/login/", methods=['GET', 'POST'])
def login():
    form=LoginForm()
    if not request.method == "POST":
        return render_template("login.html", page="Log in",form=form)

    try:
        username = form.username.data
        password = toHash(form)
    except:
        return f"""Fields not filled"""
    
    user = User.query.filter_by(username=username).first()

    if user is None:
        return f"""Doesnt exist"""
    
    if user.password == password:
        session["id"] = user.uuid
        return redirect(url_for('main'))

    return f"""Password doesnt match"""

@app.route("/log-out/", methods=["GET"])
def log_out():
    try:
        del session["id"]
    except KeyError:
        return f"""Not logged in"""
    
    return redirect(url_for('log_in'))

#endregion

@app.route("/schedule-goals/", methods=["GET", "POST"])
@login_required
def schedule_goals():
    if not request.method == "POST":
        return render_template("schedule_goals.html", page="Schedule and Goals")
    
    try:
        schedule = request.form.get("schedule")
        goals = request.form.get("goals")

        user_uuid = userId()

        for activity in schedule:
            new_activity = Activities(
                user_uuid=user_uuid,
                activity_details=activity["details"],
                start_time=activity["start_time"],
                end_time=activity["end_time"],
                day_of_week=activity["day_of_week"]
            )
            db.session.add(new_activity)

        for goal in goals:
            new_goal = MonthGoals(
                user_uuid=user_uuid,
                goal_details=goal["details"],
                hour_goal=goal.get("hour_goal"),
                month=goal["month"]
            )
            db.session.add(new_goal)
        db.session.commit()
        return jsonify({"message": "Schedule and goals saved successfully."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/process-data/", methods=["POST"])
@login_required
def process_data():
    data = request.json

    prompt = (
        "You are an AI assistant tasked with optimizing a user's weekly schedule and monthly goals. "
        "The user has provided the following data: \n"
        f"Schedule: {data['schedule']}\n"
        f"Goals: {data['goals']}\n"
        "Your task is to analyze the schedule and goals, identify any conflicts or inefficiencies, "
        "and suggest an optimized schedule and goal plan. The output must be in JSON format, "
        "structured as follows: {\"optimized_schedule\": [...], \"optimized_goals\": [...]}"
    )

    try:
        response = requests.post(
            "http://localhost:11434/api",
            json={"prompt": prompt}
        )
        response.raise_for_status()
        ai_result = response.json()
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(ai_result)



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=True)
