from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf import CSRFProtect
from flask_session import Session


app = Flask(__name__)
# 1、集成配置类
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