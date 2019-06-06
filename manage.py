"""
1、集成sqlalchemy
2、集成redis
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis

app = Flask(__name__)
class Config(object):
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/TalkingShow"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379


app.config.from_object(Config)
db = SQLAlchemy(app)
redis_sroce = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)

@app.route("/")
def index():
    redis_sroce.set("name", "laoli")
    return "index"


if __name__ == '__main__':
    app.run(debug=True)