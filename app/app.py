import logging
import os

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)


# Configure sqlalchemy
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["SQLALCHEMY_DATABASE_URI"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


@app.route('/')
def index():
    app.logger.info("greeting was requested")

    #db.drop_all()
    #db.create_all()

    from .model import Image

    #db.session.add(User(username="fred"))
    #db.session.add(User(username="jochen"))
    #db.session.commit()

    images = Image.query.all()
    app.logger.info(images)

    return render_template("greet.html", images=images)
