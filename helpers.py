from functools import wraps
from flask import redirect, session, url_for
from models import User
import re as regex
import hashlib

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not loggedIn():
            return redirect(url_for('log_in'))
        return f(*args, **kwargs)
    return decorated_function

def toHash(password):
    hash_object = hashlib.sha256()
    hash_object.update(password.encode())
    return hash_object.hexdigest()

def userId():
    try:
        return session["id"]
    except:
        return None

def loggedIn():
    if User.query.filter_by(uuid=str(userId())).first() is None and "id" in session: del session["id"]
    try:
        return "id" in session and User.query.filter_by(uuid=str(userId())).first() is not None
    except:
        return False

def hasNumber(password):
    return bool(regex.search(r"\d", password))

def hasSpecial(password):
    return bool(regex.search(r"[!@#$%^&*(),.?\":{}|<>]", password))

def calculate_time_diff(start_time, end_time):
    start = start_time.hour*60 + start_time.minute
    end = end_time.hour*60 + end_time.minute
    
    return (end - start if end >= start else (24*60) - (start - end))/60