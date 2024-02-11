from flask import Flask
import random
import frontend.common.config as config

def start():
    app = Flask(__name__)
    app.secret_key = config.dotenv["FLASK_SECRET"]

    from .main.routes import main
    from .auth.routes import create
    from .dashboard.routes import dashboard
    from .static.routes import static
    from .api.routes import api

    app.register_blueprint(main)
    app.register_blueprint(create(app))
    app.register_blueprint(dashboard)
    app.register_blueprint(static)
    app.register_blueprint(api)

    return app