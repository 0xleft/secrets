from flask import Flask
import random

def start():
    app = Flask(__name__)
    app.secret_key = random.randbytes(4096)

    from .main.routes import main
    from .auth.routes import auth
    from .admin.routes import admin
    from .static.routes import static

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(admin)
    app.register_blueprint(static)

    return app