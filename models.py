from config import db

class User(db.Model):
    __tablename__ = 'users'
    uuid = db.Column(db.String, primary_key=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)

class Activity(db.Model):
    __tablename__ = 'activities'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_uuid = db.Column(db.String, db.ForeignKey('users.uuid'), nullable=False)
    activity_details = db.Column(db.String, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    day_of_week = db.Column(db.String, nullable=False)

class MonthGoal(db.Model):
    __tablename__ = 'month_goals'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_uuid = db.Column(db.String, db.ForeignKey('users.uuid'), nullable=False)
    goal_details = db.Column(db.String, nullable=False)
    hour_goal = db.Column(db.Integer, nullable=True)
    month = db.Column(db.String, nullable=False)
