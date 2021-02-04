import logging
import os

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)


# Configure sqlalchemy
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["SQLALCHEMY_DATABASE_URI"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


@app.route('/')
def view_index():
    from .model import Image

    images = Image.query.all()
    app.logger.info(images)

    return render_template("index.html", images=images)


@app.route('/upload')
def view_upload(method=["GET", "POST"]):
    from .model import Image

    query = request.args.get("query", None)

    app.logger.info("searching %s", query)

    print("hello")

    if request.method == "POST":
        image = request.files["formFile"]
        print("hello")
        print(image.filename)

        #if request.files:
         #   f = request.files["formFile"]
          #  f.save(secure_filename(f.filename))
           # item = Image()

    return render_template("upload.html")


@app.route('/search')
def view_search():
    query = request.args.get("query", None)

    app.logger.info("searching %s", query)

    return render_template("search.html")


@app.route('/image/<string:image_id>')
def view_image(image_id):
    from .model import Image

    edit = request.args.get("edit", False)

    return render_template("image.html")


@app.route('/gallery/<int:gallery_id>')
def view_gallery(gallery_id):
    from .model import Gallery

    edit = request.args.get("edit", False)

    return render_template("gallery.html")


@app.route('/api/image/<string:image_id>')
def api_image(image_id):
    from .model import Image

    thumbnail = request.args.get('thumbnail', False)
    download = request.args.get('download', False)

    return {}
