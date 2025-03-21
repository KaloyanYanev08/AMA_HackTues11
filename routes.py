from flask import render_template, request, redirect, session, url_for, jsonify, flash
from forms import LoginForm, RegisterForm, ActivityForm, ActivityListForm
from config import app, db
from helpers import login_required, toHash, hasNumber, hasSpecial, userId,loggedIn
from models import User, Activity, MonthGoal
from datetime import datetime

@app.route("/", methods=["GET"])
def home():
    if loggedIn():
        return render_template("stats.html", page="Home")
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
        confirm_password = form.confirm_password.data
    except:
        flash("All fields must be filled", "error")
        return render_template("register.html", page="Register", form=form)
    
    if len(password) < 8 or not hasNumber(password) or not hasSpecial(password):
        flash("Password must be at least 8 characters and have at least one number and special character", "error")
        return render_template("register.html", page="Register", form=form)
    
    password = toHash(password)
    confirm_password = toHash(confirm_password)

    if password != confirm_password:
        flash("Passwords do not match", "error")
        return render_template("register.html", page="Register", form=form)

    if User.query.filter_by(username=username).first() is not None:
        flash("Username already exists", "error")
        return render_template("register.html", page="Register", form=form)
    
    user_id = str(genuuid())

    new_user = User(uuid=user_id, username=username, password=password)
    db.session.add(new_user)
    db.session.commit()

    flash("Registration successful! Please log in.", "success")
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
        flash("All fields must be filled", "error")
        return render_template("login.html", page="Log in", form=form)
    
    user = User.query.filter_by(username=username).first()

    if user is None:
        flash("User does not exist", "error")
        return render_template("login.html", page="Log in", form=form)
    
    if user.password == password:
        session["id"] = user.uuid
        return redirect(url_for('home'))

    flash("Invalid password", "error")
    return render_template("login.html", page="Log in", form=form)

@app.route("/log-out/", methods=["GET"])
@login_required
def log_out():
    try:
        del session["id"]
    except KeyError:
        return f"""Not logged in"""
    
    return redirect(url_for('log_in'))

@app.route("/create-schedule/", methods=["GET", "POST"])
@login_required
def create_schedule():
    form = ActivityListForm()

    if request.method == "POST":
        user_uuid = userId()
        try:
            # Dynamically process activities from the form data
            activities = []
            for key, value in request.form.items():
                if key.startswith("activities-"):
                    parts = key.split("-")
                    index = int(parts[1])
                    field_name = parts[2]

                    # Ensure the list is large enough to hold all activities
                    while len(activities) <= index:
                        activities.append({})

                    activities[index][field_name] = value

            # Validate and save activities
            for activity in activities:
                if not activity.get("details") or not activity.get("start_time") or not activity.get("end_time"):
                    raise Exception("All fields are required for each activity.")

                if "sleep" not in activity["details"].lower() and activity["start_time"] >= activity["end_time"]:
                    raise Exception("Start time must be less than end time.")

                # Convert start_time and end_time to Python time objects
                start_time_obj = datetime.strptime(activity["start_time"], "%H:%M").time()
                end_time_obj = datetime.strptime(activity["end_time"], "%H:%M").time()

                new_activity = Activity(
                    user_uuid=user_uuid,
                    activity_details=activity["details"],
                    start_time=start_time_obj,
                    end_time=end_time_obj,
                    day_of_week=request.form.get("day_tabs")
                )
                db.session.add(new_activity)

            db.session.commit()
            flash("Schedule created successfully!", "success")
            return redirect(url_for('home'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error saving activities: {str(e)}", "error")

    return render_template("create_schedule.html", page="Create schedule", form=form)

@app.route("/view-schedule/")
@login_required
def view_schedule():
    user_uuid = userId()
    days_of_the_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    schedule = {day: [] for day in days_of_the_week}  # Initialize all days with empty lists
    
    # Add activities to the corresponding days
    for day in days_of_the_week:
        activities = Activity.query.filter_by(user_uuid=user_uuid, day_of_week=day).all()
        if activities:
            for activity in activities:
                schedule[day].append({
                    "details": activity.activity_details,
                    "start_time": activity.start_time.strftime("%H:%M"),
                    "end_time": activity.end_time.strftime("%H:%M")
                })

    return render_template("weekly_schedule.html", page="Schedule", schedule=schedule)

@app.route("/api/process-data/", methods=["POST"])
@login_required
def process_data():
    from ai_client import send_to_model

    data = request.json

    schedule_formatted = ""
    for day, activities in data["schedule"].items():
        schedule_formatted += f"{day}:\n"
        for activity in activities:
            schedule_formatted += f"{activity['details']} from {activity['start_time']} to {activity['end_time']}\n"

    goals_formatted = ""
    for goal in data["monthly_goals"]:
        if goal.get("hour_goal"):
            goals_formatted += f"{goal['details']} for around {goal['hour_goal']} hours per week\n"
        else:
            goals_formatted += f"{goal['details']}\n"

    # Construct the prompt
    prompt = f"""
    You are an assistant with the task to modify a person's schedule to be most healthy and optimal. Optimal sleeping hours: 8 hours. Do not change work if not prompted to. Explicitly allocate time for the things the user wants. You are allowed to add exercise between activities if you are asked to add sports. For example add a quality of life improving task between them. It's also important to let people take breaks and have free time as well, so try to fit in some. The \"Monthly goal\" section applies to all days. Try to not overthink. I want you to modify the following days:
    
    {schedule_formatted}

    Monthly goals:
    {goals_formatted}

    Return the information in a JSON format, a computer will process it so don't format it for human viewing: an object with every day of the week as a key (the first letter of the day is capital), the values being lists. The lists contain objects with keys start_time, end_time and details for each activity.
    """
    try:
        json = send_to_model(prompt)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    user_uuid = userId()
    Activity.query.filter_by(user_uuid=user_uuid).delete()
    db.session.commit()

    for day, activities in json.items():
        for activity in activities:
            new_activity = Activity(
                user_uuid=user_uuid,
                activity_details=activity["details"],
                start_time=activity["start_time"],
                end_time=activity["end_time"],
                day_of_week=day
            )
            db.session.add(new_activity)
    db.session.commit()

    return jsonify(json)

@app.route("/api/get-schedule/", methods=["GET"])
@login_required
def get_schedule():
    user_uuid = userId()
    
    goals = MonthGoal.query.filter_by(user_uuid=user_uuid).all()

    days_of_the_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    schedule = {}
    for day in days_of_the_week:
        activities = Activity.query.filter_by(user_uuid=user_uuid, day_of_week=day).all()
        if len(activities) > 0: schedule[day] = []
        for activity in activities:
            schedule[day].append({
                "details": activity.activity_details,
                "start_time": activity.start_time.strftime("%H:%M"),
                "end_time": activity.end_time.strftime("%H:%M")
            })

    goals_list = [{"details": goal.goal_details, "hour_goal": goal.hour_goal} for goal in goals]

    return jsonify({"schedule": schedule, "goals": goals_list})

@app.route('/generate-schedule/', methods=['GET'])
@login_required
def generate_schedule():
    return render_template('generate_schedule.html', page="Generate schedule")