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
IMAGES_PER_PAGE = 10


def get_hash_value(img: bytes):
    from hashlib import sha256

    return sha256(img).hexdigest()


def create_thumbnail(img: bytes):
    from io import BytesIO
    from PIL import Image

    with BytesIO() as output:
        image = Image.open(BytesIO(img))

        app.logger.info(image.getexif())

        thumbnail = image.resize(THUMBNAIL_SIZE)
        thumbnail.save(output, format="jpeg")

        return output.getvalue()


def is_image_allowed(pil_image):
    return pil_image.format.lower() == "jpeg"


@app.route('/')
def view_index():
    from .model import Image

    pagination = Image.query.paginate(per_page=IMAGES_PER_PAGE)

    return render_template("index.html", pagination=pagination)


@app.route('/upload', methods=["GET", "POST"])
def view_upload():
    from flask import flash
    from io import BytesIO
    from PIL import Image as PilImage
    from sqlalchemy.exc import IntegrityError

    from .model import Image, Metadata, Thumbnail

    error = None

    if request.method == "POST":
        uploaded = request.files["formFile"]
        
        raw = uploaded.read()
        image_id = get_hash_value(raw)

        with BytesIO(raw) as raw_buffer:
            pil_image = PilImage.open(raw_buffer)

            # Check if uploaded image is jpeg using pillow
            if not is_image_allowed(pil_image):
                error = "Image does not have the appropriate format. Only jpeg is allowed."
                return render_template("upload.html", error=error)

            # Add image to database 
            image = Image()
            image.id = image_id
            image.height = image.height
            image.width = image.width
            image.description = request.form["description"]
            image.content = raw

            # Generate thumbnail and add to database
            image.thumbnail = Thumbnail()
            image.thumbnail.content = create_thumbnail(raw)

            # List exif metadata
            for key, value in pil_image.getexif().items():
                image.meta.append(Metadata(key=key, value=str(value)))

            db.session.add(image)

            try:
                db.session.commit()
                flash("Image was successfully uploaded!")

            except IntegrityError:
                error = "We already have this image in our database."

    return render_template("upload.html", error=error)


@app.route('/search')
def view_search():
    from .model import Image

    # TODO: this fails if the query contains a whitespace
    query = request.args.get("query", None)
    page = request.args.get("page", None)
    if page:
        page = int(page)

    app.logger.info("searching %s", query)

    # https://docs.sqlalchemy.org/en/14/dialects/postgresql.html#full-text-search
    pagination = Image.query.filter(Image.description.match(query)).paginate(page=page, per_page=IMAGES_PER_PAGE)

    return render_template("search.html", pagination=pagination, query=query)


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


@app.errorhandler(404)
def view_404(e):
    return render_template("404.html"), 404


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
