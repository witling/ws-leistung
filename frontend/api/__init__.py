from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from io import BytesIO
from PIL import Image as PilImage

from model import *


api = Blueprint('api', __name__)


@api.route("/api/galleries")
def api_galleries():
    from flask import jsonify

    galleries = Gallery.query.all()

    return jsonify(list(map(lambda gallery: gallery.as_dict, galleries)))


@api.route("/api/gallery/<int:gallery_id>/add")
def api_gallery_add_image(gallery_id):
    image_id = request.args["image_id"]
    gallery = Gallery.query.filter_by(id=gallery_id).first_or_404()

    gallery_image = GalleryImage(image_id=image_id, gallery_id=gallery_id)
    gallery.images.append(gallery_image)

    db.session.commit()

    return {}


@api.route("/api/gallery/<int:gallery_id>/remove")
def api_gallery_remove_image(gallery_id):
    image_id = request.args["image_id"]

    gallery_image = GalleryImage.query.filter_by(image_id=image_id, gallery_id=gallery_id).first_or_404()
    db.session.delete(gallery_image)
    db.session.commit()

    flash("Image was removed from gallery.", category="success");

    return redirect(url_for("site.view_gallery", gallery_id=gallery_id))


@api.route("/api/gallery/<int:gallery_id>/delete")
def api_gallery_delete(gallery_id):
    gallery = Gallery.query.filter_by(id=gallery_id).first_or_404()
    db.session.delete(gallery)
    db.session.commit()

    flash("Gallery was deleted.", category="success")

    return redirect(url_for("site.view_index"))


@api.route("/api/image/<string:image_id>")
def api_image(image_id):
    from flask import Response

    thumbnail = request.args.get("thumbnail", False)
    download = request.args.get("download", False)

    # Determine whether the thumbnail or the original image was requested
    if not thumbnail:
        image = Image.query.filter_by(id=image_id).first_or_404()
    else:
        image = Thumbnail.query.filter_by(image_id=image_id).first_or_404()

    response = Response(image.content, mimetype="image/jpeg")

    # If a download was requested, add `Content-Disposition` header
    if download:
        if not thumbnail:
            file_name = "{}.jpeg".format(image.id)
        else:
            file_name = "{}_thumb.jpeg".format(image.image_id)

        response.headers["Content-Disposition"] = "attachment; filename=\"{}\"".format(file_name)

    return response


@api.route("/api/image/<string:image_id>/delete")
def api_image_delete(image_id):
    image = Image.query.filter_by(id=image_id).first_or_404()
    db.session.delete(image)
    db.session.commit()

    flash("Image was deleted.", category="success")

    return redirect(url_for("site.view_index"))

