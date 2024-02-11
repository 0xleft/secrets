from flask import render_template, request, Blueprint, redirect, url_for, session, jsonify
import pymongo
from ..common.config import dotenv, PER_PAGE_COUNT
from functools import wraps
from flask import session, redirect, url_for, flash

client = pymongo.MongoClient(dotenv["MONGO_URI"])
db = client["secrets"]

api = Blueprint("api", __name__)

def logged_in(count=True):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth = request.headers.get("Authorization")
            if auth is None:
                return jsonify({"error": "Unauthorized"}), 401
            user = db["users"].find_one({"api_key": auth})
            if user is None:
                return jsonify({"error": "Unauthorized"}), 401
            if user["is_deleted"]:
                return jsonify({"error": "Unauthorized"}), 401
            if user["api_key_uses_left"] < 1:
                return jsonify({"error": "No uses left"}), 403
            if count:
                db["users"].update_one({"api_key": auth}, {"$inc": {"api_key_uses_left": -1}})
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@api.route("/secrets/api/health", methods=["GET"])
@logged_in(False)
def api_health():
    return jsonify({"status": "ok"})

@api.route("/secrets/api/search", methods=["GET"])
@logged_in()
def api_search():
    # get from params
    params = request.args

    query = {}
    if "url" in params:
        query["url"] = {"$regex": params["url"]}
    if "commit" in params:
        query["commit"] = {"$regex": params["commit"]}
    if "path" in params:
        query["path"] = {"$regex": params["path"]}
    if "secret" in params:
        query["secret"] = {"$regex": params["secret"]}
    if "match" in params:
        query["match"] = {"$regex": params["match"]}
    if "rule_id" in params:
        query["rule_id"] = {"$regex": params["rule_id"]}
    if "owner" in params:
        query["owner"] = {"$regex": params["owner"]}
    if "date" in params:
        query["date"] = {"$regex": params["date"]}

    page = params.get("page", 1)
    try:
        page = int(page)
        if page < 1:
            page = 1
    except:
        page = 1

    results = db["secrets"].find(query, limit=100, skip=(page - 1) * PER_PAGE_COUNT)
    return jsonify([{
        "url": result["url"],
        "commit": result["commit"],
        "path": result["path"],
        "secret": result["secret"],
        "match": result["match"],
        "rule_id": result["rule_id"],
        "owner": result["owner"],
        "date": result["date"]
    } for result in list(results)])

@api.route("/secrets/api/user", methods=["GET"])
@logged_in(False)
def api_user():
    pass