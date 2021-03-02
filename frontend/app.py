import os

from common.fmt import dateformat
from common import database

from flask import Blueprint, current_app, flash, Flask, render_template, request

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

    @app.errorhandler(500)
    def view_500(e):
        return render_template("500.html"), 500
    
    
    @app.errorhandler(404)
    def view_404(e):
        return render_template("404.html"), 404


    @api_proxy.route("/<path:url>", methods=["GET", "POST"])
    def api_proxy_route(url):
        from flask import redirect, url_for

        fetch_backend(url, request.method)

        if url.endswith("remove"):
            return redirect(url_for("site.view_gallery", gallery_id=gallery_id))

        return redirect(url_for("site.view_index"))


    app.register_blueprint(api)
    app.register_blueprint(site)

    return app


if __name__ == "__main__":
    create_app("dev").run()
