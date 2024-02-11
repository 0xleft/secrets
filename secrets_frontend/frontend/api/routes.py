from flask import render_template, request, Blueprint, redirect, url_for, session, jsonify
import pymongo
from ..common.config import dotenv
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
                db["users"].update_one({"api_key": auth}, {"$dec": {"api_key_uses_left": 1}})
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@logged_in(False)
@api.route("/secrets/api/health", methods=["GET", "POST"])
def api_health():
    return jsonify({"status": "ok"})

@logged_in()
@api.route("/secrets/api/search", methods=["GET", "POST"])
def api_search():
    pass

@logged_in(False)
@api.route("/secrets/api/user", methods=["GET", "POST"])
def api_user():
    pass