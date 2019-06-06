"""
1、集成sqlalchemy
"""




from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)


@app.route("/")
def index():
    return "index"


if __name__ == '__main__':
    app.run(debug=True)