from flask import Flask, render_template
from sqlalchemy import create_engine

app = Flask(__name__)

@app.route('/')
def hello_world():
    engine = create_engine("postgresql://achim:passw0rd@db/datenbank")

    with engine.connect() as con:
        print(con.info)

    return render_template("greet.html")
