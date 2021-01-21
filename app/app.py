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
def hello_world():
    app.logger.info("greeting was requested")

    """
    db.drop_all()
    db.create_all()

    from .model import User

    db.session.add(User(username="fred"))
    db.session.add(User(username="jochen"))
    db.session.commit()

    app.logger.info(User.query.all())
    """

    return render_template("greet.html")
