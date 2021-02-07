from datetime import datetime
from flask_serialize import FlaskSerializeMixin

from database import db


class Image(db.Model):
    __tablename__ = "images"

    id = db.Column(db.String(32), primary_key=True)
    description = db.Column(db.String(255))
    added_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    height = db.Column(db.Integer)
    width = db.Column(db.Integer)
    content = db.Column(db.LargeBinary)

    # one-to-one relationship
    thumbnail = db.relationship("Thumbnail", backref="image", lazy=True, uselist=False, cascade="all, delete")

    # one-to-many relationship
    meta = db.relationship("Metadata", backref="image", lazy=True, cascade="all, delete")


class Thumbnail(db.Model):
    __tablename__ = "thumbnails"

    id = db.Column(db.String(32), db.ForeignKey("images.id"), primary_key=True)
    content = db.Column(db.LargeBinary)


class Metadata(db.Model):
    __tablename__ = "metadata"

    id = db.Column(db.String(32), db.ForeignKey("images.id"), primary_key=True)
    key = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(255))


class Gallery(FlaskSerializeMixin, db.Model):
    __tablename__ = "galleries"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))
    added_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    images = db.relationship("GalleryImage", lazy=True, cascade="all, delete")


class GalleryImage(FlaskSerializeMixin, db.Model):
    __tablename__ = "galleries_images"

    gallery_id = db.Column(db.Integer, db.ForeignKey("galleries.id"), primary_key=True)
    image_id = db.Column(db.String(32), db.ForeignKey("images.id"), primary_key=True)

    image = db.relationship("Image", lazy=True)
