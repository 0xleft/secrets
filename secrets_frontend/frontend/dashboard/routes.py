from flask import render_template, request, Blueprint, redirect, url_for, session, jsonify
import pymongo
from ..common.config import dotenv, PER_PAGE_COUNT, DEFAULT_KEY_USES
import math
from ..common.utils import generate_api_key

client = pymongo.MongoClient(dotenv["MONGO_URI"])
db = client["secrets"]

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/secrets/user')
def user():
    if "id" not in session:
        return redirect(url_for("auth.login"))

    user = db["users"].find_one({"id": session["id"]})

    scans = list(db["scans"].find({"user_id": session["id"]}).sort("date", -1))
    return render_template("user.html", user=user, scans=scans, search={"status": "", "url": "", "org": ""}, page=1, page_end=(math.ceil(len(scans) / PER_PAGE_COUNT)))

@dashboard.route('/secrets/user', methods=["POST"])
def user_post():
    if "id" not in session:
        return redirect(url_for("auth.login"))
    
    if "delete_account" in request.form:
        db["users"].update_one({"id": session["id"]}, {"$set": {"is_deleted": True}})
        return redirect(url_for("auth.logout"))
    elif "reset_key" in request.form:
        db["users"].update_one({"id": session["id"]}, {"$set": {"api_key": generate_api_key()}})
    elif "delete_scan" in request.form:
        url = request.form.get("url")
        db["scans"].delete_one({"url": url, "user_id": session["id"]})
    elif "search" in request.form:
        status = request.form.get("status")
        page = request.form.get("page")
        if page is None:
            page = 1
        else:
            try:
                page = int(page)
                if page < 1:
                    page = 1
            except:
                page = 1
        url = request.form.get("url")
        org = request.form.get("org")

        query = {}
        if status != "":
            query["status"] = status
        if url != "":
            query["url"] = {"$regex": url}
        if org != "":
            query["org"] = {"$regex": org}

        scans = list(db["scans"].find(query).sort("date", -1).limit(PER_PAGE_COUNT).skip((page-1)*PER_PAGE_COUNT))
        return render_template("user.html", user=db["users"].find_one({"id": session["id"]}), scans=scans, search={"status": status, "url": url, "org": org}, page=page, page_end=(math.ceil(len(scans) / PER_PAGE_COUNT)))
    
    return redirect(url_for("dashboard.user"))

@dashboard.route('/secrets/admin', methods=["GET"])
def admin():
    if "id" not in session:
        return redirect(url_for("auth.login"))
    
    if session["is_admin"] != True:
        return redirect(url_for("main.index"))
    
    # find user where api_key is not null
    users = list(db["users"].find())
    info = db["info"].find_one()
    return render_template("admin.html", users=users, info=info, search="", page=1, page_end=(math.ceil(len(users) / PER_PAGE_COUNT)))

@dashboard.route('/secrets/admin', methods=["POST"])
def admin_post():
    if "id" not in session:
        return redirect(url_for("auth.login"))
    
    if session["is_admin"] != True:
        return redirect(url_for("main.index"))
    
    if "delete_all_users" in request.form:
        db["users"].delete_many({})
    elif "delete_all_secrets" in request.form:
        db["secrets"].delete_many({})
        db["info"].delete_one({})
    elif "update_user" in request.form:
        
        user_id = request.form.get("update_user")
        username = request.form.get("username")
        is_deleted = request.form.get("is_deleted")
        is_admin = request.form.get("is_admin")
        api_key = request.form.get("api_key")
        api_key_uses_left = request.form.get("api_key_uses_left")
        if user_id is not None and username is not None and is_deleted is not None and is_admin is not None and api_key is not None and api_key_uses_left is not None:
            db["users"].update_one({"id": int(user_id)}, {"$set": {
                "login": username,
                "is_deleted": is_deleted == "True",
                "is_admin": is_admin == "True",
                "api_key": api_key,
                "api_key_uses_left": int(api_key_uses_left)
            }})

    elif "search" in request.form:
        search = request.form.get("username")
        page = request.form.get("page")
        if page is None:
            page = 1
        else:
            try:
                page = int(page)
                if page < 1:
                    page = 1
            except:
                page = 1

        users = list(db["users"].find({"login": {"$regex": search}}, limit=PER_PAGE_COUNT, skip=(page-1)*PER_PAGE_COUNT))
        info = db["info"].find_one()
        return render_template("admin.html", users=users, info=info, search=search, page=page, page_end=(math.ceil(len(users) / PER_PAGE_COUNT)))
    
    return redirect(url_for("dashboard.admin"))