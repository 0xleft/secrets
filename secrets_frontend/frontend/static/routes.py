from flask import Blueprint, send_from_directory

static = Blueprint('static', __name__)

@static.route('/secrets/static/<path:filename>')
def static_files(filename):
    return send_from_directory('files', filename)