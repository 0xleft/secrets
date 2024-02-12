from flask import render_template, request, Blueprint, redirect, url_for, session, jsonify
import pymongo
from ..common.config import dotenv, PER_PAGE_COUNT
from functools import wraps
from flask import session, redirect, url_for, flash
import math
import re
import hashlib
import requests
import json

client = pymongo.MongoClient(dotenv["MONGO_URI"])
db = client["secrets"]

api = Blueprint("api", __name__)

def logged_in(should_count=True):
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
			if should_count:
				db["users"].update_one({"api_key": auth}, {"$inc": {"api_key_uses_left": -1}})
			return f(*args, **kwargs)
		return decorated_function
	return decorator

@api.route("/secrets/api/health", methods=["GET"])
@logged_in(should_count=False)
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

	end = math.ceil(db["info"].find_one()["secret_count"] / PER_PAGE_COUNT)
	if page > end:
		page = end
	results = db["secrets"].find(query, limit=PER_PAGE_COUNT, skip=(page-1)*PER_PAGE_COUNT)
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
@logged_in(should_count=False)
def api_user():
	user = db["users"].find_one({"api_key": request.headers.get("Authorization")})
	return jsonify({
		"id": user["id"],
		"login": user["login"],
		"email": user["email"],
		"is_admin": user["is_admin"],
		"api_key_uses_left": user["api_key_uses_left"]
	})

@api.route("/secrets/api/scan_org", methods=["GET"])
@logged_in()
def api_scan_org():
	user = db["users"].find_one({"api_key": request.headers.get("Authorization")})

	org = request.args.get("org")
	if org is None or org == "":
		return jsonify({"error": "Invalid request"}), 400

	repos = requests.get(f"https://api.github.com/orgs/{org}/repos", headers={"Authorization": f"token {dotenv['GITHUB_TOKEN']}"})
	if repos.status_code != 200:
		return jsonify({"error": "Invalid org"}), 400
	repos = repos.json()
	scan_count = 0
	for repo in repos:
		scan = db["scans"].find_one({"url": repo["html_url"], "user_id": user["id"]})
		if scan is not None:
			continue
		db["scans"].insert_one({"url": repo["html_url"], "user_id": user["id"], "org": org, "status": "pending", "secrets": []})
		scan_count += 1

	db["users"].update_one({"api_key": request.headers.get("Authorization")}, {"$inc": {"api_key_uses_left": -scan_count}})

	return jsonify({"status": "ok"})

@api.route("/secrets/api/scan", methods=["GET"])
@logged_in()
def api_scan():
	user = db["users"].find_one({"api_key": request.headers.get("Authorization")})

	url = request.args.get("url")
	if url is None or url == "":
		return jsonify({"error": "Invalid request"}), 400

	if not re.match(r"^https:\/\/github.com\/[^\/]+\/[^\/]+", url):
		return jsonify({"error": "Invalid URL, please use https form"}), 400
	
	scan = db["scans"].find_one({"url": url, "user_id": user["id"]})
	if scan is not None:
		if scan["status"] == "done":
			return jsonify({"error": "Already scanned"}), 400
		else:
			return jsonify({"error": "Scan pending"}), 400
	
	db["scans"].insert_one({"url": url, "user_id": user["id"], "status": "pending", "secrets": []})
	
	return jsonify({"status": "ok"})

@api.route("/secrets/api/scan/info", methods=["GET"])
@logged_in(should_count=False)
def api_scan_status():
	user = db["users"].find_one({"api_key": request.headers.get("Authorization")})
	
	url = request.args.get("url")
	if url is None or url == "":
		return jsonify({"error": "Invalid request"}), 400

	scan = db["scans"].find_one({"url": url, "user_id": user["id"]})
	if scan is None:
		return jsonify({"status": "not found"}), 404
	if scan["status"] != "done":
		return jsonify({"status": scan["status"]}), 200
	return jsonify({
		"status": scan["status"],
		"secrets": [{
			"commit": secret["commit"],
			"path": secret["path"],
			"secret": secret["secret"],
			"match": secret["match"],
			"rule_id": secret["rule_id"],
			"owner": secret["owner"],
			"date": secret["date"],
			"org": secret["org"] if "org" in secret else ""
		} for secret in scan["secrets"]]
	})

@api.route("/secrets/api/scan_org/get_scans", methods=["GET"])
@logged_in(should_count=False)
def api_scan_org_get_scans():
	user = db["users"].find_one({"api_key": request.headers.get("Authorization")})

	org = request.args.get("org")
	if org is None or org == "":
		return jsonify({"error": "Invalid request"}), 400

	scans = db["scans"].find({"org": org, "user_id": user["id"]})
	return jsonify([{
		"url": scan["url"],
		"status": scan["status"]
	} for scan in scans])