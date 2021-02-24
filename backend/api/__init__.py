from flask import Blueprint, current_app, flash, jsonify, redirect, render_template, request, url_for
from werkzeug.exceptions import HTTPException
from io import BytesIO
from PIL import Image as PilImage

from model import *

THUMBNAIL_SIZE = (256, 256)
EXIF_DATE_CREATED = 36867
IMAGES_PER_PAGE = 9

api = Blueprint('api', __name__)


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


@api.route("/api/search")
def api_search():
    from sqlalchemy import or_

    querystring = request.args.get("query", None)

    if " " in querystring:
        querytext = querystring.replace(" ", ",")
    else:
        querytext = querystring

    page = request.args.get("page", 1)
    if page:
        page = int(page)

    current_app.logger.info("searching %s", querystring)

    # https://docs.sqlalchemy.org/en/14/dialects/postgresql.html#full-text-search

    query = Image.query.filter(or_(SearchPool.value.ilike(f"%{querystring}%"), SearchPool.value.match(querytext)))
    query = query.join(SearchPool, Image.id == SearchPool.image_id)
    query = query.distinct(SearchPool.image_id)

    pagination = query.paginate(page=page, per_page=IMAGES_PER_PAGE)
    pages = list(pagination.iter_pages())
    results = list(map(lambda item: item.as_dict, pagination.items))
    end = pages[-1] if pages else 1
    result = {"start": 1, "end": end, "page": page, "results": results}

    return jsonify(result)


@api.route("/api/galleries")
def api_galleries():
    from flask import jsonify

    galleries = Gallery.query.all()

    return jsonify(list(map(lambda gallery: gallery.as_dict, galleries)))


@api.route("/api/gallery/<int:gallery_id>/<string:image_id>", methods=["POST", "DELETE"])
def api_gallery_image(gallery_id, image_id):
    if request.method == "POST":
        gallery = Gallery.query.filter_by(id=gallery_id).first_or_404()
        gallery_image = GalleryImage(image_id=image_id, gallery_id=gallery_id)
        gallery.images.append(gallery_image)

    elif request.method == "DELETE":
        gallery_image = GalleryImage.query.filter_by(image_id=image_id, gallery_id=gallery_id).first_or_404()
        db.session.delete(gallery_image)

    try:
        db.session.commit()

    except:
        return {}, 500

    return {}


@api.route("/api/gallery", methods=["POST"])
@api.route("/api/gallery/<int:gallery_id>", methods=["PUT", "DELETE"])
def api_gallery(gallery_id=None):
    if not gallery_id and request.method == "POST":
        db.session.add(create_gallery(request))

    else:
        gallery = Gallery.query.filter_by(id=gallery_id).first_or_404()

        if request.method == "PUT":
            update_gallery(gallery, request)

        elif request.method == "DELETE":
            db.session.delete(gallery)

    try:
        db.session.commit()

    except:
        return {}, 500

    return {}


@api.route("/api/image", methods=["POST"])
@api.route("/api/image/<string:image_id>", methods=["PUT", "DELETE"])
def api_image(image_id=None):
    if not image_id and request.method == "POST":
        db.session.add(create_image(request))

    else:
        image = Image.query.filter_by(id=image_id).first_or_404()

        if request.method == "PUT":
            update_image(image, request)

        elif request.method == "DELETE":
            db.session.delete(image)

    try:
        db.session.commit()

    except:
        return {}, 500
    
    return {}


def create_gallery(request):
    current_app.logger.info(request.form)

    gallery = Gallery()
    update_gallery(gallery, request)

    tag_names = list(request.form.getlist('tag'))

    query = Image.query.join(Tag, Tag.image_id == Image.id)
    query = query.filter(Tag.name.in_(tag_names))

    for image in query.all():
        gallery_image = GalleryImage(image_id=image.id, gallery_id=gallery.id)
        gallery.images.append(gallery_image)

    db.session.add(gallery)

    return gallery


def update_gallery(gallery, request):
    gallery.name = request.form["galleryName"]
    gallery.description = request.form["galleryDescription"]


def create_image(request):
    uploaded = request.files["formFile"]
    raw = uploaded.read()

    if not raw:
        raise Exception("The uploaded file was invalid.")

    image_id = get_hash_value(raw)

    with BytesIO(raw) as raw_buffer:
        pil_image = PilImage.open(raw_buffer)

        # Check if uploaded image is jpeg using pillow
        if not is_image_allowed(pil_image):
            raise Exception("Image does not have the appropriate format. Only jpeg is allowed.")

        
        # If taken date was specified in the form, prefer it over exif data
        taken_date_str = request.form.get("takenDate")
        taken_date = None

        if taken_date_str:
            taken_date = datetime.strptime(taken_date_str, '%Y-%m-%d')
        else:
            # The date and time when the original image data was generated
            taken_date_str = pil_image.getexif().get(EXIF_DATE_CREATED)
            if taken_date_str:
                taken_date = datetime.strptime(taken_date_str, '%Y:%m:%d %H:%M:%S')

        width, height = pil_image.size

        # Add image to database 
        image = Image()
        image.id = image_id
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


        return image


def update_image(image, request):
    image.description = request.form["description"]

    # parse tags according to rules e.g. split at ','; replace whitespace with '-'
    new_tag_names = parse_tag_names(request.form["tags"])

    image.update_tags(new_tag_names)
