"""
1、集成配置类
2、集成sqlalchemy     pip install flask_sqlalchemy
3、集成redis          pip install flask_redis
4、集成CRSFProtect
5、集成flask_session  pip install flask_session
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf import CSRFProtect
from flask_session import Session

app = Flask(__name__)
# 1、集成配置类
class Config(object):
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/TalkingShow"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    SESSION_TYPE = "redis"
    SESSION_KEY_PREFIX = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    SESSION_USE_SIGNER = True
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = 86400 * 2


app.config.from_object(Config)
# ２、集成sqlalchemy
db = SQLAlchemy(app)
# ３、集成redis
redis_sroce = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
# ４、集成CSRFProtect
CSRFProtect(app)
# 5、集成Session
# 说明：flask中Session是用户保存用户数据的容器（上下文），而flask_session是指定session指定保存路径
Session(app)






@app.route("/")
def index():
    redis_sroce.set("name", "laoli")
    return "index"


if __name__ == '__main__':
    app.run(debug=True)