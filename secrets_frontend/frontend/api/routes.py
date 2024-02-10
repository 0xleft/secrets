from flask import render_template, request, Blueprint, redirect, url_for, session, jsonify
import pymongo
from ..common.config import dotenv

client = pymongo.MongoClient(dotenv["MONGO_URI"])
db = client["secrets"]

api = Blueprint('api', __name__)

@api.route('/secrets/api/health', methods=['GET', 'POST'])
def api_health():
    pass