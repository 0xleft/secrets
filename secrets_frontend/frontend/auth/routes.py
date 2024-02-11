from flask import render_template, request, Blueprint, redirect, url_for, session, jsonify
import pymongo
from ..common.config import dotenv, DEFAULT_KEY_USES
import hashlib
from authlib.integrations.flask_client import OAuth
import datetime
import random
from ..common.utils import generate_api_key

client = pymongo.MongoClient(dotenv["MONGO_URI"])
db = client["secrets"]

auth = Blueprint("auth", __name__)

github = None
oauth = None

def create(app):
    global github, oauth
    oauth = OAuth(app)
    github = oauth.register(
        name='github',
        client_id=dotenv["GITHUB_CLIENT_ID"],
        client_secret=dotenv["GITHUB_CLIENT_SECRET"],
        access_token_url='https://github.com/login/oauth/access_token',
        access_token_params=None,
        authorize_url='https://github.com/login/oauth/authorize',
        authorize_params=None,
        api_base_url='https://api.github.com/',
        client_kwargs={'scope': 'user:email'},
    )
    return auth

@auth.route("/secrets/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if "id" in session:
            return redirect(url_for("main.index"))

        return render_template("login.html")
    else:
        if dotenv["DEV"] == "1":
            return github.authorize_redirect(url_for("auth.authorize", _external=True, ))
        else:
            return github.authorize_redirect("https://pageup.lt/secrets/github/callback")

@auth.route('/secrets/github/callback')
def authorize():
    global github
    print(request.args)
    token = github.authorize_access_token()
    resp = github.get("user", token=token)
    profile = resp.json()

    user = db["users"].find_one({"id": profile["id"]})
    if user is not None and user["is_deleted"] == True and not user["is_admin"]:
        return redirect(url_for("auth.login"), error="Account is deleted")
    if user is None:
        if dotenv["CAN_REGISTER"] == "0" and not int(profile["id"]) == int(dotenv["ADMIN_ID"]):
            return redirect(url_for("auth.login", error="Registration is temporarely disabled"))
        resp = github.get("user/emails", token=token)
        emails = resp.json()
        email = None
        for e in emails:
            if e["primary"] == True and e["verified"] == True:
                email = e["email"]
                break
        if email is None:
            return redirect(url_for("auth.login"))
        
        db["users"].insert_one({
            "id": profile["id"],
            "login": profile["login"],
            "is_admin": int(profile["id"]) == int(dotenv["ADMIN_ID"]),
            "email": email,
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now(),
            "api_key": generate_api_key(),
            "api_key_uses_left": DEFAULT_KEY_USES,
            "last_ip": "",
            "is_deleted": False
        })

    session["id"] = int(profile["id"])
    session["login"] = profile["login"]
    session["email"] = profile["email"]
    session["is_admin"] = int(profile["id"]) == int(dotenv["ADMIN_ID"])
    session["logged_in"] = True
    
    db["users"].update_one({"id": profile["id"]}, {"$set": {"updated_at": datetime.datetime.now()}})
    if "X-Forwarded-For" in request.headers:
        ip = request.headers["X-Forwarded-For"]
    else:
        ip = request.remote_addr
    db["users"].update_one({"id": profile["id"]}, {"$set": {"last_ip": ip}})
    return redirect(url_for("main.index"))

@auth.route("/secrets/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect(url_for("main.index"))