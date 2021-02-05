import logging
import os

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.secret_key = b"89?_!30xc0vy03#+34+2+"


# Configure sqlalchemy
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["SQLALCHEMY_DATABASE_URI"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

THUMBNAIL_SIZE = (256, 256)


def get_hash_value(img: bytes):
    from hashlib import sha256

    return sha256(img).hexdigest()


def create_thumbnail(img: bytes):
    from io import BytesIO
    from PIL import Image

    with BytesIO() as output:
        image = Image.open(BytesIO(img))

        thumbnail = image.resize(THUMBNAIL_SIZE)
        thumbnail.save(output, format="jpeg")

        return output.getvalue()


@app.route('/')
def view_index():
    from .model import Image

    images = Image.query.all()

    return render_template("index.html", images=images)


@app.route('/upload', methods=["GET", "POST"])
def view_upload():
    from flask import flash
    from sqlalchemy.exc import IntegrityError
    from .model import Image, Thumbnail

    error = None

    if request.method == "POST":
        uploaded = request.files["formFile"]

        raw = uploaded.read()
        image_id = get_hash_value(raw)

        image = Image()
        image.id = image_id
        image.name = uploaded.filename
        image.description = 'Beschreibung'
        image.content = raw

        image.thumbnail = Thumbnail()
        image.thumbnail.content = create_thumbnail(raw)

        db.session.add(image)


        try:
            db.session.commit()
            flash("Image was successfully uploaded!")

        except IntegrityError:
            error = "We already have this image in our database."

    return render_template("upload.html", error=error)


@app.route('/search')
def view_search():
    query = request.args.get("query", None)

    app.logger.info("searching %s", query)

    # https://docs.sqlalchemy.org/en/14/dialects/postgresql.html#full-text-search

    return render_template("search.html")


@app.route('/image/<string:image_id>')
def view_image(image_id):
    from .model import Image

    edit = request.args.get("edit", False)

    image = Image.query.filter_by(id=image_id).first()

    return render_template("image.html", image=image, edit=edit)


@app.route('/gallery')
@app.route('/gallery/<int:gallery_id>')
def view_gallery(gallery_id=None):
    from .model import Gallery

    edit = request.args.get("edit", False)

    return render_template("gallery.html")


@app.route('/api/image/<string:image_id>')
def api_image(image_id):
    from flask import Response

    from .model import Image, Thumbnail

    thumbnail = request.args.get('thumbnail', False)
    download = request.args.get('download', False)

    if not thumbnail:
        image = Image.query.filter_by(id=image_id).first()
        file_name = "{}.jpeg".format(image.id)
    else:
        image = Thumbnail.query.filter_by(id=image_id).first()
        file_name = "{}_thumb.jpeg".format(image.id)

    response = Response(image.content, mimetype='image/jpeg')

    if download:
        response.headers["Content-Disposition"] = "attachment; filename=\"{}\"".format(file_name)

    return response
