import os

from flask import flash, Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

from .fmt import dateformat

app = Flask(__name__)
app.secret_key = b"89?_!30xc0vy03#+34+2+"

# Configure custom jinja2 filters
app.jinja_env.filters["dateformat"] = dateformat

# Configure sqlalchemy
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["SQLALCHEMY_DATABASE_URI"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

THUMBNAIL_SIZE = (256, 256)
IMAGES_PER_PAGE = 9


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


def is_image_allowed(pil_image):
    return pil_image.format.lower() == "jpeg"


@app.errorhandler(404)
def view_404(e):
    return render_template("404.html"), 404


@app.route("/")
def view_index():
    from .model import GalleryImage, Image

    pagination = Image.query.paginate(per_page=IMAGES_PER_PAGE)

    return render_template("index.html", pagination=pagination)


@app.route("/upload", methods=["GET", "POST"])
def view_upload():
    from io import BytesIO
    from PIL import Image as PilImage
    from sqlalchemy.exc import IntegrityError

    from .model import GalleryImage, Image, Metadata, Thumbnail

    # Upload was initiated
    if request.method == "POST":
        uploaded = request.files["formFile"]

        raw = uploaded.read()
        image_id = get_hash_value(raw)

        with BytesIO(raw) as raw_buffer:
            pil_image = PilImage.open(raw_buffer)

            # Check if uploaded image is jpeg using pillow
            if not is_image_allowed(pil_image):
                flash("Image does not have the appropriate format. Only jpeg is allowed.", category="error")
                return render_template("upload.html")

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
                flash("Image was successfully uploaded!", category="success")

            except IntegrityError:
                flash("We already have this image in our database.", category="error")

    return render_template("upload.html")


@app.route("/search")
def view_search():
    from .model import GalleryImage, Image
    from sqlalchemy import or_

    querystring = request.args.get("query", None)

    if " " in querystring:
        query = querystring.replace(" ", ",")
    else:
        query = querystring

    page = request.args.get("page", None)
    if page:
        page = int(page)

    app.logger.info("searching %s", query)

    # https://docs.sqlalchemy.org/en/14/dialects/postgresql.html#full-text-search
    pagination = Image.query.filter(or_(Image.description.contains(query), Image.description.match(query))).paginate(page=page, per_page=IMAGES_PER_PAGE)

    return render_template("search.html", pagination=pagination, query=querystring)


@app.route("/image/<string:image_id>", methods=["GET", "POST"])
def view_image(image_id):
    from .model import GalleryImage, Image

    image = Image.query.filter_by(id=image_id).first()

    # Image was updated
    if request.method == "POST":
        try:
            image.description = request.form["description"]
            db.session.commit()

            flash("The image was updated.", category="success")

        except Exception as e:
            app.logger.warning(e)
            flash("There was an error while updating.", category="error")

        return render_template("image.html", image=image, edit=False)

    edit = request.args.get("edit", False)

    return render_template("image.html", image=image, edit=edit)


@app.route("/galleries", methods=["GET", "POST"])
def view_galleries():
    from .model import Gallery

    edit = request.args.get("edit", False)

    # Gallery was updated
    if request.method == "POST":
        app.logger.info(request.form)

        gallery = Gallery()
        gallery.name = request.form["galleryName"]
        gallery.description = request.form["galleryDescription"]

        db.session.add(gallery)

        try:
            db.session.commit()
            flash("Gallery was created.", category="success")

        except Exception as e:
            flash("There was an error while creating a new gallery.", category="error")
            app.logger.info(e)

    pagination = Gallery.query.order_by(Gallery.id.desc()).paginate(per_page=IMAGES_PER_PAGE)

    return render_template("galleries.html", pagination=pagination, edit=edit)


@app.route("/gallery/<int:gallery_id>", methods=["GET", "POST"])
def view_gallery(gallery_id):
    from flask import redirect, url_for

    from .model import Gallery, GalleryImage

    edit = request.args.get("edit", False)

    gallery = Gallery.query.filter_by(id=gallery_id).first()
    pagination = GalleryImage.query.filter_by(gallery_id=gallery_id).paginate(per_page=IMAGES_PER_PAGE)

    if request.method == "POST":
        gallery.name = request.form["name"]
        gallery.description = request.form["description"]

        try:
            db.session.commit()
            flash("Gallery was updated.", category="success")

        except Exception as e:
            app.logger.warning(e)
            flash("There was an error while updating.", category="error")


    return render_template("gallery.html", gallery=gallery, pagination=pagination, edit=edit)


@app.route("/gallery/<int:gallery_id>/delete")
def view_gallery_delete(gallery_id):
    from flask import redirect, url_for

    from .model import Gallery, GalleryImage

    gallery = Gallery.query.filter_by(id=gallery_id).first()
    db.session.delete(gallery)
    db.session.commit()

    flash("Gallery was deleted.", category="success")

    return redirect(url_for("view_galleries"))


@app.route("/api/galleries")
def api_galleries():
    from flask import jsonify

    from .model import Gallery

    galleries = Gallery.query.all()

    return jsonify(list(map(lambda gallery: gallery.as_dict, galleries)))


@app.route("/api/gallery/<int:gallery_id>/add")
def api_gallery_add_image(gallery_id):
    from .model import Gallery, GalleryImage

    image_id = request.args["image_id"]
    gallery = Gallery.query.filter_by(id=gallery_id).first()

    gallery_image = GalleryImage(image_id=image_id, gallery_id=gallery_id)
    gallery.images.append(gallery_image)

    db.session.commit()

    return {}


@app.route("/api/gallery/<int:gallery_id>/remove")
def api_gallery_remove_image(gallery_id):
    from flask import redirect, url_for

    from .model import Gallery, GalleryImage

    image_id = request.args["image_id"]

    gallery_image = GalleryImage.query.filter_by(image_id=image_id, gallery_id=gallery_id).first()
    db.session.delete(gallery_image)
    db.session.commit()

    flash("Image was removed from gallery.", category="success");

    return redirect(url_for("view_gallery", gallery_id=gallery_id))


@app.route("/api/gallery/<int:gallery_id>/export")
def api_gallery_export(gallery_id):
    from flask import jsonify

    from .model import Gallery

    gallery = Gallery.query.filter_by(id=gallery_id).first();
    file_name = "gallery_{}.json".format(gallery.id)

    response = jsonify(gallery.as_dict)
    response.headers["Content-Disposition"] = "attachment; filename=\"{}\"".format(file_name)

    return response


@app.route("/api/image/<string:image_id>")
def api_image(image_id):
    from flask import Response

    from .model import Image, Thumbnail

    thumbnail = request.args.get("thumbnail", False)
    download = request.args.get("download", False)

    # Determine whether the thumbnail or the original image was requested
    if not thumbnail:
        image = Image.query.filter_by(id=image_id).first()
    else:
        image = Thumbnail.query.filter_by(id=image_id).first()

    response = Response(image.content, mimetype="image/jpeg")

    # If a download was requested, add `Content-Disposition` header
    if download:
        if not thumbnail:
            file_name = "{}.jpeg".format(image.id)
        else:
            file_name = "{}_thumb.jpeg".format(image.id)

        response.headers["Content-Disposition"] = "attachment; filename=\"{}\"".format(file_name)

    return response
