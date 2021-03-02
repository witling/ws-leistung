from datetime import datetime
from flask_serialize import FlaskSerializeMixin
from typing import List

from database import db


class Image(db.Model):
    __tablename__ = "images"

    id = db.Column(db.String(32), primary_key=True)
    description = db.Column(db.String(255))
    added_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    taken_date = db.Column(db.DateTime)
    height = db.Column(db.Integer)
    width = db.Column(db.Integer)
    content = db.Column(db.LargeBinary)

    # one-to-one relationship
    thumbnail = db.relationship("Thumbnail", backref="image", lazy=True, uselist=False, cascade="all, delete")

    # one-to-many relationship
    meta = db.relationship("Metadata", backref="image", lazy=True, cascade="all, delete")

    # one-to-many relationship
    tags = db.relationship("Tag", lazy=True, cascade="save-update, merge, delete, delete-orphan")

    # one-to-many relationship
    gallery_images = db.relationship("GalleryImage", lazy=True, cascade="all, delete")

    def url(self, download=False):
        if download:
            return '/api/image/{}?download=1'.format(self.id)
        return '/api/image/{}'.format(self.id)

    def thumbnail_url(self, download=False):
        if download:
            return '/api/image/{}?thumbnail=1&download=1'.format(self.id)
        return '/api/image/{}?thumbnail=1'.format(self.id)

    def tags_to_str(self):
        return ', '.join(map(lambda tag: tag.name, self.tags))

    def update_tags(self, tag_names: List[str]):
        # `reversed` avoids loop corruption, because we modify the list
        for tag in reversed(self.tags):
            # If the image has this tag but it is not in the new tag list
            if tag.name not in tag_names:
                # Remove it
                self.tags.remove(tag)
            else:
                # The image has the tag and it is also in the new tag list ->
                # Do nothing
                tag_names.remove(tag.name)

        # Create all tags that weren't present on the image already
        for tag_name in tag_names:
            if tag_name:
                self.tags.append(Tag(name=tag_name))


class Thumbnail(db.Model):
    __tablename__ = "thumbnails"

    image_id = db.Column(db.String(32), db.ForeignKey("images.id"), primary_key=True)
    content = db.Column(db.LargeBinary)


class Metadata(db.Model):
    __tablename__ = "metadata"

    image_id = db.Column(db.String(32), db.ForeignKey("images.id"), primary_key=True)
    key = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(255))


class Tag(db.Model):
    __tablename__ = "tags"

    image_id = db.Column(db.String(32), db.ForeignKey("images.id"), primary_key=True)
    name = db.Column(db.String(16), primary_key=True)


class Gallery(FlaskSerializeMixin, db.Model):
    __tablename__ = "galleries"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))
    added_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    images = db.relationship("GalleryImage", lazy=True, cascade="all, delete")

    def preview_images(self):
        query = Image.query.join(GalleryImage).filter_by(gallery_id=self.id).limit(3)
        return query.all()


class GalleryImage(FlaskSerializeMixin, db.Model):
    __tablename__ = "galleries_images"

    gallery_id = db.Column(db.Integer, db.ForeignKey("galleries.id"), primary_key=True)
    image_id = db.Column(db.String(32), db.ForeignKey("images.id"), primary_key=True)

    image = db.relationship("Image", lazy=True)


class SearchPool(db.Model):
    __tablename__ = "search_pool"

    image_id = db.Column(db.String(32), primary_key=True)
    value = db.Column(db.String(), primary_key=True)
