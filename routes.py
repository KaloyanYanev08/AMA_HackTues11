from flask import render_template, request, redirect, session, url_for, jsonify
from forms import LoginForm, RegisterForm, ActivityForm, ScheduleGoalsForm
from datetime import datetime
from config import app, db
from helpers import login_required, toHash, hasNumber, hasSpecial, userId,loggedIn
from models import User, Activity, MonthGoal

@app.route("/", methods=["GET"])
def home():
    return render_template("home.html", page="Home")

@app.route("/register/", methods=["GET", "POST"])
def register():
    if loggedIn():
        return redirect(url_for('home'))
    form=RegisterForm()
    if not request.method == "POST":
        return render_template("register.html", page="Register",form=form)
    
    from uuid import uuid4 as genuuid

    try:
        username = form.username.data
        password = form.password.data
        confirm_password = form.confirm_password.data  # Corrected to fetch confirm_password from the form
    except:
        return f"""Fields not filled"""
    
    if len(password) < 8 or not hasNumber(password) or not hasSpecial(password):
        return f"""Pasword be at least 8 characters and have at least one number and special character"""
    
    password = toHash(password)
    confirm_password=toHash(confirm_password)

    if password != confirm_password:
        return f"""Passwords do not match"""

    if User.query.filter_by(username=username).first() is not None:
        return f"""User exists"""
    
    user_id = str(genuuid())

    new_user = User(uuid=user_id, username=username, password=password)
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('log_in'))

@app.route("/log-in/", methods=["GET", "POST"])
def log_in():
    if loggedIn():
        return redirect(url_for('home'))
    form=LoginForm()
    if not request.method == "POST":
        return render_template("login.html", page="Log in", form=form)

    try:
        username = form.username.data
        password = toHash(form.password.data)
    except:
        return f"""Fields not filled"""
    
    user = User.query.filter_by(username=username).first()

    if user is None:
        return f"""Doesnt exist"""
    
    if user.password == password:
        session["id"] = user.uuid
        return redirect(url_for('home'))

    return f"""Password doesnt match"""

@app.route("/log-out/", methods=["GET"])
@login_required
def log_out():
    try:
        del session["id"]
    except KeyError:
        return f"""Not logged in"""
    
    return redirect(url_for('log_in'))

@app.route("/schedule-goals/", methods=["GET", "POST"])
@login_required
def schedule_goals():
    if not request.method == "POST":
        return render_template("schedule_goals.html", page="Schedule and Goals")
    
    try:
        schedule = request.form.get("schedule")
        goals = request.form.get("goals")

        user_uuid = userId()

        for day,activity in schedule:
            new_activity = Activity(
                user_uuid=user_uuid,
                activity_details=activity["details"],
                start_time=activity["start_time"],
                end_time=activity["end_time"],
                day_of_week=activity["day_of_week"]
            )
            db.session.add(new_activity)

        for goal in goals:
            new_goal = MonthGoal(
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

@app.route("/create_schedule/", methods=["GET", "POST"])
@login_required
def create_schedule():
    form = ScheduleGoalsForm()

    if form.add_more.data and request.method == "POST":  # Handle adding more activities
        form.activities.append_entry()
        return render_template("schedule.html", page="Schedule", form=form)

    if form.validate_on_submit():  # Handle form submission
        user_uuid = userId()
        try:
            for activity in form.activities.data:
                new_activity = Activity(
                    user_uuid=user_uuid,
                    activity_details=activity["details"],
                    start_time=activity["start_time"],
                    end_time=activity["end_time"],
                    day_of_week=activity["day_of_week"],
                    date=activity["date"]
                )
                db.session.add(new_activity)
            db.session.commit()
            return redirect(url_for('home'))  # Redirect to home after saving
        except Exception as e:
            db.session.rollback()
            # Debugging: Log the error
            print(f"Error saving activities: {str(e)}")
            return f"An error occurred: {str(e)}", 500

    # Debugging: Log form errors if validation fails
    if form.errors:
        print(f"Form errors: {form.errors}")

    return render_template("schedule.html", page="Schedule", form=form)

@app.route("/process-data/", methods=["POST"])
@login_required
def process_data():
    from ai_client import send_to_model

    data = request.json

    days_map = {"1": "Monday", "2": "Tuesday", "3": "Wednesday", "4": "Thursday", "5": "Friday", "6": "Saturday", "7": "Sunday"}
    schedule_formatted = ""
    for day, activities in data["schedule"].items():
        schedule_formatted += f"{days_map[day]}:\n"
        for activity in activities:
            schedule_formatted += f"{activity['details']}: {activity['start_time']} to {activity['end_time']}\n"

    goals_formatted = ""
    for goal in data["monthly_goals"]:
        if goal["hour_goal"]:
            goals_formatted += f"{goal['details']} for around {goal['hour_goal']} hours per week\n"
        else:
            goals_formatted += f"{goal['details']}\n"

    # Construct the prompt
    prompt = f"""
    You are an assistant with the task to modify a person's schedule to be most healthy and optimal. Optimal sleeping hours: 8 hours. Do not change work if not prompted to. Explicitly allocate time for the things the user wants. You are allowed to add exercise between activities if you are asked to add sports. For example add a quality of life improving task between them. It's also important to let people take breaks and have free time as well, so try to fit in some. The "Monthly goal" section applies to all days. Try to not overthink. I want you to modify the following days:
    
    {schedule_formatted}

    Monthly goals:
    {goals_formatted}

    Return the information in a JSON format, a computer will process it so don't format it for human viewing: an object with every day of the week as a number, the values being lists. The lists contain objects with keys start_time, end_time and details for each activity.
    """

    return send_to_model(prompt)