from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from werkzeug.exceptions import HTTPException 
from io import BytesIO
from PIL import Image as PilImage
    
from model import *


site = Blueprint('site', __name__)

IMAGES_PER_PAGE = 9

def fetch_backend(route, flask_request=None, method='GET'):
    import requests

    url = f"http://backend:5000{route}"

    current_app.logger.info(f"requesting backend url: {url}")

    if flask_request:
        res = requests.request(method, url, data=flask_request.form, files=flask_request.files)
    else:
        res = requests.request(method, url)

    if res.status_code != 200:
        raise HTTPException(res.status_code)

    return res


@site.route("/")
def view_index():
    pagination = Image.query.paginate(per_page=IMAGES_PER_PAGE)
    return render_template("index.html", pagination=pagination)


@site.route("/upload", methods=["GET", "POST"])
def view_upload():
    # Upload was initiated
    if request.method == "POST":
        try:
            fetch_backend("/api/image", request, method="POST")
            flash("Image was successfully uploaded!", category="success")

        except:
            flash("We already have this image in our database.", category="error")

    return render_template("upload.html")


@site.route("/search")
def view_search():
    from sqlalchemy import or_

    querystring = request.args.get("query", None)

    if " " in querystring:
        querytext = querystring.replace(" ", ",")
    else:
        querytext = querystring

    page = request.args.get("page", None)
    if page:
        page = int(page)

    current_app.logger.info("searching %s", querystring)

    # https://docs.sqlalchemy.org/en/14/dialects/postgresql.html#full-text-search

    query = Image.query.filter(or_(SearchPool.value.ilike(f"%{querystring}%"), SearchPool.value.match(querytext)))
    query = query.join(SearchPool, Image.id == SearchPool.image_id)
    query = query.distinct(SearchPool.image_id)

    pagination = query.paginate(page=page, per_page=IMAGES_PER_PAGE)

    return render_template("search.html", pagination=pagination, query=querystring)


@site.route("/image/<string:image_id>", methods=["GET", "POST"])
def view_image(image_id):
    edit = request.args.get("edit", False)

    # Image was updated
    if request.method == "POST":
        try:
            fetch_backend(f"/api/image/{image_id}", request, method="PUT")
            flash("The image was updated.", category="success")

        except Exception as e:
            current_app.logger.warning(e)
            flash("There was an error while updating.", category="error")

        edit = False

    image = Image.query.filter_by(id=image_id).first_or_404()

    return render_template("image.html", image=image, edit=edit)


@site.route("/galleries", methods=["GET", "POST"])
def view_galleries():
    edit = request.args.get("edit", False)

    # Gallery should be created
    if request.method == "POST":
        try:
            fetch_backend(f"/api/gallery", request, method="POST")
            flash("Gallery was created.", category="success")

        except Exception as e:
            flash("There was an error while creating a new gallery.", category="error")
            current_app.logger.warning(e)

    pagination = Gallery.query.order_by(Gallery.id.desc()).paginate(per_page=IMAGES_PER_PAGE)
    tags = Tag.query.distinct(Tag.name).all()

    return render_template("galleries.html", pagination=pagination, tags=tags, edit=edit)


@site.route("/gallery/<int:gallery_id>", methods=["GET", "POST"])
def view_gallery(gallery_id):
    edit = request.args.get("edit", False)

    # Gallery was updated
    if request.method == "POST":
        try:
            fetch_backend(f"/api/gallery/{gallery_id}", request, method="PUT")
            flash("Gallery was updated.", category="success")

        except Exception as e:
            current_app.logger.warning(e)
            flash("There was an error while updating.", category="error")

    gallery = Gallery.query.filter_by(id=gallery_id).first_or_404()
    pagination = GalleryImage.query.filter_by(gallery_id=gallery_id).paginate(per_page=IMAGES_PER_PAGE)

    return render_template("gallery.html", gallery=gallery, pagination=pagination, edit=edit)
