from flask import render_template, request, Blueprint, redirect, url_for, session, jsonify
import pymongo
from ..common.config import dotenv

client = pymongo.MongoClient(dotenv["MONGO_URI"])
db = client["secrets"]

dashboard = Blueprint('admin', __name__)

@dashboard.route('/secrets/user')
def user():
    if "id" not in session:
        return redirect(url_for("auth.login"))

    user = db["users"].find_one({"id": session["id"]})
    return render_template("user.html", user=user)

@dashboard.route('/secrets/admin', methods=["GET"])
def admin():
    if "id" not in session:
        return redirect(url_for("auth.login"))
    
    if session["is_admin"] != True:
        return redirect(url_for("main.index"))
    
    # find user where api_key is not null
    users = list(db["users"].find())
    api_key_users = list(db["users"].find({"api_key": {"$ne": None}}))
    info = db["info"].find_one()
    return render_template("admin.html", users=users, api_key_users=api_key_users, info=info)

@dashboard.route('/secrets/admin', methods=["POST"])
def admin_post():
    if "id" not in session:
        return redirect(url_for("auth.login"))
    
    if session["is_admin"] != True:
        return redirect(url_for("main.index"))
    
    if request.form.get("action") == "delete_user":
        user_id = request.form.get("delete_user")
        db["users"].delete_one({"id": user_id})
    elif request.form.get("action") == "delete_all_users":
        db["users"].delete_many({})
    elif request.form.get("action") == "delete_all_secrets":
        db["secrets"].delete_many({})
        db["info"].delete_one({})
    elif request.form.get("action") == "reset_key_uses":
        user_id = request.form.get("reset_key_uses")
        db["users"].update_one({"id": user_id}, {"$set": {"api_key_uses_left": 0}})

    return redirect(url_for("dashboard.admin"))