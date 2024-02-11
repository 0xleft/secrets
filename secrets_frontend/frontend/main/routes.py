from flask import render_template, request, Blueprint, redirect, url_for, session, jsonify
import pymongo
from ..common.config import dotenv, PER_PAGE_COUNT, MAX_PAGE_COUNT
import math

client = pymongo.MongoClient(dotenv["MONGO_URI"])
db = client["secrets"]

main = Blueprint('main', __name__)

@main.route('/secrets/')
def index():
    repo_count = db["info"].find_one()["repo_count"]
    secret_count = db["info"].find_one()["secret_count"]
    return render_template("index.html", repo_count=repo_count, secret_count=secret_count)

@main.route('/secrets/search', methods=['GET', 'POST'])
def search():
    if request.method == "GET":
        return render_template("search.html", secrets=None, result_count=0, url="", commit="", path="", secret="", match="", rule_id="", owner="", date="", page=1, page_end=0, page_start=0, PER_PAGE_COUNT=PER_PAGE_COUNT)
    url = request.form.get("url", "")
    commit = request.form.get("commit", "")
    path = request.form.get("path", "")
    secret = request.form.get("secret", "")
    match = request.form.get("match", "")
    rule_id = request.form.get("rule_id", "")
    owner = request.form.get("owner", "")
    date = request.form.get("date", "")
    page = request.form.get("page", 1)
    try:
        page = int(page)
        if page < 1:
            page = 1
    except:
        page = 1

    query = {}
    if url != "":
        query["url"] = url
    if commit != "":
        query["commit"] = commit
    if path != "":
        query["path"] = path
    if secret != "":
        query["secret"] = secret
    if match != "":
        query["match"] = match
    if rule_id != "":
        query["rule_id"] = rule_id
    if owner != "":
        query["owner"] = owner
    if date != "":
        query["date"] = date

    page_end = min(math.ceil(db["info"].find_one()["secret_count"] / PER_PAGE_COUNT), MAX_PAGE_COUNT)
    results = db["secrets"].find(query if session.get("logged_in") is not None else {}, limit=PER_PAGE_COUNT, skip=(page-1)*PER_PAGE_COUNT)
    results_count = len(list(results.clone()))
    return render_template("search.html", secrets=enumerate(results), page=page, page_end=page_end, page_start=0, result_count=results_count, PER_PAGE_COUNT=PER_PAGE_COUNT, url=url, commit=commit, path=path, secret=secret, match=match, rule_id=rule_id, owner=owner, date=date)

@main.route('/secrets/docs', methods=['GET', 'POST'])
def docs():
    return redirect(url_for('static.static_files', filename='docs/index.html'))