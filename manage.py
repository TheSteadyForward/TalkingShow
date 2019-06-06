"""
1、集成配置类
2、集成sqlalchemy     pip install flask_sqlalchemy
3、集成redis          pip install flask_redis
4、集成CRSFProtect    pip install falsk_wtf
5、集成flask_session  pip install flask_session
6、集成falsk_script   pip install falsk_script
7、集成flask_migrate  pip install falsk_migrate
"""
from flask import Flask,session
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf import CSRFProtect
from flask_session import Session
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand


# 1、集成配置类
class Config(object):
    SECRET_KEY = "1234567890"
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/TalkingShow"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    # 指定储存数据库
    SESSION_TYPE = "redis"
    # 指定储存session对象
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    # 是否设置session　加密
    SESSION_USE_SIGNER = True
    #　设置session不是永久保存
    SESSION_PERMANENT = False
    # 设置session保存时间
    PERMANENT_SESSION_LIFETIME = 86400 * 2

app = Flask(__name__)

app.config.from_object(Config)
# ２、集成sqlalchemy
db = SQLAlchemy(app)
# ３、集成redis
redis_srore = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
# ４、集成CSRFProtect
CSRFProtect(app)
# 5、集成flask_session
# 说明：flask中Session是用户保存用户数据的容器（上下文），而flask_session是指定session指定保存路径
Session(app)
# 6、集成falsk_manager
manager = Manager(app)
# 7、集成flask_migrate
Migrate(app, db)
manager.add_command("db", MigrateCommand)


@app.route("/")
def index():
    # redis_sroce.set("name", "小花")
    session["age"] = "小花"
    return "index"


if __name__ == '__main__':
    manager.run()