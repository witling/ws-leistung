from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from io import BytesIO
from PIL import Image as PilImage
    
from .model import *

site = Blueprint('site', __name__)

THUMBNAIL_SIZE = (256, 256)
IMAGES_PER_PAGE = 9


def get_hash_value(img: bytes):
    from hashlib import sha256

    return sha256(img).hexdigest()


def create_thumbnail(img: bytes):
    with BytesIO() as output:
        image = PilImage.open(BytesIO(img))

        thumbnail = image.resize(THUMBNAIL_SIZE)
        thumbnail.save(output, format="jpeg")

        return output.getvalue()


def is_image_allowed(pil_image):
    return pil_image.format.lower() == "jpeg"


def parse_tag_names(raw: str):
    tags = []

    for part in raw.lower().split(','):
        name = part.strip().replace(' ', '-')

        if name:
            tags.append(name)

    return tags


@site.errorhandler(404)
def view_404(e):
    return render_template("404.html"), 404


@site.route("/")
def view_index():
    pagination = Image.query.paginate(per_page=IMAGES_PER_PAGE)

    return render_template("index.html", pagination=pagination)


@site.route("/upload", methods=["GET", "POST"])
def view_upload():
    from sqlalchemy.exc import IntegrityError

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

            # 36867 - The date and time when the original image data was generated
            taken_date_exif = pil_image.getexif().get(36867)
            taken_date = request.form["takenDatePicker"]
            width, height = pil_image.size

            # Add image to database 
            image = Image()
            image.id = image_id
            if taken_date is "":
                if not taken_date_exif is None:
                    image.taken_date = datetime.strptime(taken_date_exif, '%Y:%m:%d %H:%M:%S')
            else:
                image.taken_date = taken_date
            image.height = height
            image.width = width
            image.description = request.form["description"]
            image.content = raw

            # Set tags on image
            new_tag_names = parse_tag_names(request.form["tags"])
            image.update_tags(new_tag_names)

            # Generate thumbnail and add to database
            image.thumbnail = Thumbnail()
            image.thumbnail.content = create_thumbnail(raw)

            # List exif metadata
            for key, raw_value in pil_image.getexif().items():
                try:
                    if isinstance(raw_value, bytes):
                        value = raw_value.decode("utf-8", errors="replace").replace("\x00", "\uFFFD")
                    else:
                        value = str(raw_value)

                    image.meta.append(Metadata(key=key, value=value))

                except UnicodeDecodeError:
                    current_app.logger.warning("cannot decode value for key %d", key)


            db.session.add(image)

            try:
                db.session.commit()
                flash("Image was successfully uploaded!", category="success")

            except IntegrityError:
                flash("We already have this image in our database.", category="error")

    return render_template("upload.html")


@site.route("/search")
def view_search():
    from sqlalchemy import or_, func

    querystring = request.args.get("query", None)

    if " " in querystring:
        query = querystring.replace(" ", ",")
    else:
        query = querystring

    page = request.args.get("page", None)
    if page:
        page = int(page)

    current_app.logger.info("searching %s", query)

    # https://docs.sqlalchemy.org/en/14/dialects/postgresql.html#full-text-search
    # pagination = Image.query.filter(or_(func.lower(Image.description).contains(func.lower(query)), Image.description.match(query))).paginate(page=page, per_page=IMAGES_PER_PAGE)
    pagination = Image.query.filter(
        or_(Image.tags.any(or_(Tag.name.contains(func.lower(query)), Tag.name.match(query))), func.lower(Image.description).contains(func.lower(query)), Image.description.match(query))).paginate(
        page=page, per_page=IMAGES_PER_PAGE)

    return render_template("search.html", pagination=pagination, query=querystring)


@site.route("/image/<string:image_id>", methods=["GET", "POST"])
def view_image(image_id):
    image = Image.query.filter_by(id=image_id).first_or_404()

    # Image was updated
    if request.method == "POST":
        try:
            image.description = request.form["description"]

            # parse tags according to rules e.g. split at ','; replace whitespace with '-'
            new_tag_names = parse_tag_names(request.form["tags"])

            image.update_tags(new_tag_names)

            db.session.commit()

            flash("The image was updated.", category="success")

        except Exception as e:
            current_app.logger.warning(e)
            flash("There was an error while updating.", category="error")

        return render_template("image.html", image=image, edit=False)

    edit = request.args.get("edit", False)

    return render_template("image.html", image=image, edit=edit)


@site.route("/image/<string:image_id>/delete")
def view_image_delete(image_id):
    image = Image.query.filter_by(id=image_id).first_or_404()
    db.session.delete(image)
    db.session.commit()

    flash("Image was deleted.", category="success")

    return redirect(url_for("site.view_index"))


@site.route("/galleries", methods=["GET", "POST"])
def view_galleries():
    edit = request.args.get("edit", False)

    # Gallery was updated
    if request.method == "POST":
        current_app.logger.info(request.form)

        gallery = Gallery()
        gallery.name = request.form["galleryName"]
        gallery.description = request.form["galleryDescription"]

        db.session.add(gallery)

        try:
            db.session.commit()
            flash("Gallery was created.", category="success")

        except Exception as e:
            flash("There was an error while creating a new gallery.", category="error")
            current_app.logger.info(e)

    pagination = Gallery.query.order_by(Gallery.id.desc()).paginate(per_page=IMAGES_PER_PAGE)

    tags = Tag.query.distinct(Tag.name).all()

    return render_template("galleries.html", pagination=pagination, tags=tags, edit=edit)


@site.route("/gallery/<int:gallery_id>", methods=["GET", "POST"])
def view_gallery(gallery_id):
    edit = request.args.get("edit", False)

    gallery = Gallery.query.filter_by(id=gallery_id).first_or_404()
    pagination = GalleryImage.query.filter_by(gallery_id=gallery_id).paginate(per_page=IMAGES_PER_PAGE)

    if request.method == "POST":
        gallery.name = request.form["name"]
        gallery.description = request.form["description"]

        try:
            db.session.commit()
            flash("Gallery was updated.", category="success")

        except Exception as e:
            current_app.logger.warning(e)
            flash("There was an error while updating.", category="error")


    return render_template("gallery.html", gallery=gallery, pagination=pagination, edit=edit)


@site.route("/gallery/<int:gallery_id>/delete")
def view_gallery_delete(gallery_id):
    gallery = Gallery.query.filter_by(id=gallery_id).first_or_404()
    db.session.delete(gallery)
    db.session.commit()

    flash("Gallery was deleted.", category="success")

    return redirect(url_for("site.view_index"))


@site.route("/api/galleries")
def api_galleries():
    from flask import jsonify

    galleries = Gallery.query.all()

    return jsonify(list(map(lambda gallery: gallery.as_dict, galleries)))


@site.route("/api/gallery/<int:gallery_id>/add")
def api_gallery_add_image(gallery_id):
    image_id = request.args["image_id"]
    gallery = Gallery.query.filter_by(id=gallery_id).first_or_404()

    gallery_image = GalleryImage(image_id=image_id, gallery_id=gallery_id)
    gallery.images.append(gallery_image)

    db.session.commit()

    return {}


@site.route("/api/gallery/<int:gallery_id>/remove")
def api_gallery_remove_image(gallery_id):
    image_id = request.args["image_id"]

    gallery_image = GalleryImage.query.filter_by(image_id=image_id, gallery_id=gallery_id).first_or_404()
    db.session.delete(gallery_image)
    db.session.commit()

    flash("Image was removed from gallery.", category="success");

    return redirect(url_for("site.view_gallery", gallery_id=gallery_id))


@site.route("/api/gallery/<int:gallery_id>/export")
def api_gallery_export(gallery_id):
    from flask import jsonify

    gallery = Gallery.query.filter_by(id=gallery_id).first_or_404();
    file_name = "gallery_{}.json".format(gallery.id)

    response = jsonify(gallery.as_dict)
    response.headers["Content-Disposition"] = "attachment; filename=\"{}\"".format(file_name)

    return response


@site.route("/api/image/<string:image_id>")
def api_image(image_id):
    from flask import Response

    thumbnail = request.args.get("thumbnail", False)
    download = request.args.get("download", False)

    # Determine whether the thumbnail or the original image was requested
    if not thumbnail:
        image = Image.query.filter_by(id=image_id).first_or_404()
    else:
        image = Thumbnail.query.filter_by(id=image_id).first_or_404()

    response = Response(image.content, mimetype="image/jpeg")

    # If a download was requested, add `Content-Disposition` header
    if download:
        if not thumbnail:
            file_name = "{}.jpeg".format(image.id)
        else:
            file_name = "{}_thumb.jpeg".format(image.id)

        response.headers["Content-Disposition"] = "attachment; filename=\"{}\"".format(file_name)

    return response
