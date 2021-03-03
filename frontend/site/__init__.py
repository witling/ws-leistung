from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from werkzeug.exceptions import HTTPException 
    
from common.fetch import fetch_backend
from common.model import *

site = Blueprint('site', __name__)

IMAGES_PER_PAGE = 9

class JsonPaginator:
    def __init__(self, json):
        def to_image(item):
            item["added_date"] = datetime.strptime(item["added_date"], '%Y-%m-%d')

            if item["taken_date"]:
                item["taken_date"] = datetime.strptime(item["taken_date"], '%Y-%m-%d')

            return Image(**item)

        self.page = json["page"]
        self.items = map(to_image, json["results"])
        self._start = json["start"]
        self._end = json["end"]

    def iter_pages(self):
        return (i + 1 for i in range(self._end))


@site.route("/")
def view_index():
    pagination = Image.query.paginate(per_page=IMAGES_PER_PAGE)
    return render_template("index.html", pagination=pagination)


@site.route("/upload", methods=["GET", "POST"])
def view_upload():
    status_code = 200

    # Upload was initiated
    if request.method == "POST":
        try:
            fetch_backend("/api/image", request, method="POST")
            flash("Image was successfully uploaded!", category="success")

        except Exception as e:
            status_code = 500
            current_app.logger.error(e)
            flash("We already have this image in our database.", category="error")

    return render_template("upload.html"), status_code


@site.route("/search")
def view_search():
    querystring = request.args.get("query", None)
    res = fetch_backend("/api/search", request)

    body = res.json()

    date_filter = body.get("filter", None)
    pagination = JsonPaginator(body)

    # keep query params for pagination
    url_query = ["query=" + querystring]

    if date_filter:
        url_query.append("filterDate=" + date_filter["date"])
        url_query.append("filterDateCondition=" + date_filter["condition"])

    url_query = '&'.join(url_query)

    return render_template("search.html", pagination=pagination, query=querystring, date_filter=date_filter, url_query=url_query)


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
