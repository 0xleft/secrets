from frontend import start
from flask_wtf.csrf import CSRFProtect
import waitress
from frontend.common.config import dotenv

csrf = CSRFProtect()

app = start()

if __name__ == '__main__':
    csrf.init_app(app)

    if dotenv["DEV"] == "1":
        app.run(debug=True, port=9434, host="0.0.0.0")
    else:
        waitress.serve(app, port=9434)