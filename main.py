from flask import Flask, render_template, request, jsonify, redirect, session, url_for #type: ignore
from flask_sqlalchemy import SQLAlchemy #type: ignore
from functools import wraps
from uuid import uuid4 as genuuid
import re as regex
import hashlib

app = Flask(__name__)
app.secret_key = "TESTING_TESTING_123"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

@app.route("/", methods=["GET"])
@app.route("/home", methods=["GET"])
def main():
    return render_template("home.html", page="home")


@app.route("/register/", methods=['GET', 'POST'])
def register():
    return render_template("register.html", page="register")

if __name__ == "__main__":
    app.run(debug=True)


