import os

from common.fmt import dateformat
from common import database

from flask import flash, Flask, render_template, request

from .api import api

def create_app(config):
    app = Flask(__name__)
    app.secret_key = b"89?_!30xc0vy03#+34+2+"
    
    # Configure custom jinja2 filters
    app.jinja_env.filters["dateformat"] = dateformat
    
    # Configure sqlalchemy
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["SQLALCHEMY_DATABASE_URI"]
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    database.init_app(app)

    @app.route("/load-spec")
    def load_spec():
        from pathlib import Path
        swagger_json = Path(__file__).parent / "static/swagger.json"
        return open(swagger_json, "r").read()

    app.register_blueprint(api)

    return app


if __name__ == "__main__":
    create_app("dev").run()
