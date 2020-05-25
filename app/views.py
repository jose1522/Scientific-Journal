from app import app
from flask import render_template, url_for, session, jsonify, make_response, g, redirect, abort, flash
from app.objects.integration.sendGrid import EmailCategory,Email
from flask import request as req
from functools import wraps
import json


def login_required(f):
    # method wraps other functions
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'userName' in session: #if there is a user key in the session object, continue
            return f(*args, **kwargs)
        else:
            return redirect(url_for('index'))
    return wrap

@app.route("/")
def index():
    session['user'] = 'Test'
    res = make_response("Hello World")
    res.set_cookie("genericCookie", json.dumps({"key1":"value1","key2":"value2"}))
    return res

@app.route("/user")
def displayUser():
    return session['user']

@app.route("/logout")
def logout():
    session.clear()
    return "Goodbye World!"