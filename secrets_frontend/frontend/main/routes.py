from flask import render_template, request, Blueprint, redirect, url_for, session, jsonify
import pymongo
from ..common.config import dotenv

client = pymongo.MongoClient(dotenv["MONGO_URI"])
db = client["secrets"]

main = Blueprint('main', __name__)

@main.route('/secrets')
def index():
    repo_count = db["info"].find_one()["repo_count"]
    secret_count = db["info"].find_one()["secret_count"]
    return render_template("index.html", repo_count=repo_count, secret_count=secret_count)

@main.route('/secrets/search', methods=['GET', 'POST'])
def search():
    pass

@main.route('/secrets/docs', methods=['GET', 'POST'])
def docs():
    pass