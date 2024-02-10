from flask import render_template, request, Blueprint, redirect, url_for, session, jsonify
import pymongo
from ..common.config import dotenv

client = pymongo.MongoClient(dotenv["MONGO_URI"])
db = client["secrets"]

auth = Blueprint('auth', __name__)

@auth.route('/secrets/login', methods=['GET', 'POST'])
def login():
    pass

@auth.route('/secrets/register', methods=['GET', 'POST'])
def register():
    if dotenv["CAN_REGISTER"] == "0":
        return redirect(url_for("auth.login"))
    pass