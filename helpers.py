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
    try:
        return "id" in session and User.query.filter_by(uuid=str(userId())).first() is not None
    except:
        return False

def hasNumber(password):
    return bool(regex.search(r"\d", password))

def hasSpecial(password):
    return bool(regex.search(r"[!@#$%^&*(),.?\":{}|<>]", password))