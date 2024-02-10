from flask import render_template, request, Blueprint, redirect, url_for, session, jsonify
import pymongo
from ..common.config import dotenv

client = pymongo.MongoClient(dotenv["MONGO_URI"])
db = client["secrets"]

admin = Blueprint('admin', __name__)

@admin.route('/secrets/admin')
def index():
    pass