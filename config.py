from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.secret_key = "TESTING_TESTING_123"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Enable CSRF protection
csrf = CSRFProtect(app)

from models import *

with app.app_context():
    db.create_all()

ollama_endpoint = "http://localhost:11434"
ollama_model = "deepseek-r1:14b"