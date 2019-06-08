import logging
from redis import StrictRedis


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


class DevelopConfig(Config):
    DEBUG = True
    LOGGING_LEVEL = logging.DEBUG

class ProductionConfig(Config):
    DEBUG = False
    LOGGING_LEVEL = logging.WARNING


class TestConfig(Config):
    DEBUG = True
    LOGGING_LEVEL = logging.DEBUG

config = {
    "develop":DevelopConfig,
    "production":ProductionConfig,
    "test":TestConfig
}