import os

from common.fetch import fetch_backend
from common.fmt import dateformat
from common import database

from flask import Blueprint, current_app, flash, Flask, render_template, request
from flask_swagger_ui import get_swaggerui_blueprint

from .api import api
from .site import site

def create_app(config):
    app = Flask(__name__)
    api_proxy = Blueprint("api-proxy", __name__)

    app.secret_key = b"89?_!30xc0vy03#+34+2+"
    
    # Configure custom jinja2 filters
    app.jinja_env.filters["dateformat"] = dateformat
    
    # Configure sqlalchemy
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["SQLALCHEMY_DATABASE_URI"]
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    database.init_app(app)

    @app.route("/load-spec-frontend")
    def load_spec_frontend():
        from pathlib import Path
        swagger_json = Path(__file__).parent / "static/swagger.json"
        return open(swagger_json, "r").read()


    @app.route("/load-spec-backend")
    def load_spec_backend():
        return fetch_backend("/load-spec").json()


    @app.errorhandler(500)
    def view_500(e):
        return render_template("500.html"), 500
    
    
    @app.errorhandler(404)
    def view_404(e):
        return render_template("404.html"), 404


    app.register_blueprint(api)
    app.register_blueprint(site)

    app.register_blueprint(create_swaggerui(config, "frontend"))
    app.register_blueprint(create_swaggerui(config, "backend"))

    return app


def create_swaggerui(config, service):
    from pathlib import Path

    swagger_json = Path(__file__).parent / "static/swagger.json"

    return get_swaggerui_blueprint(
        f"/docs/{service}",
        f"http://localhost:4000/load-spec-{service}",
        blueprint_name = f"swaggerui-{service}",
        config = {
            "app_name": f"Image archive | {service}",
        }
    )


if __name__ == "__main__":
    create_app("dev").run()
