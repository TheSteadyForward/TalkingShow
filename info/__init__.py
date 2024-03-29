import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from config import config
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_session import Session

from info.utils.common import do_index_class


def set_logging(config_name):
    # 设置日志的记录等级
    logging.basicConfig(level=config[config_name].LOGGING_LEVEL) # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)



db = SQLAlchemy()
# 为了能让redis_store正常使用，先定义一个全局变量，然后在函数中进行全局变量修改声明
redis_store = None # type:StrictRedis

def set_config(config_name):
    set_logging(config_name)
    app = Flask(__name__)
    # 1、集成配置类
    app.config.from_object(config[config_name])
    # ２、集成sqlalchemy
    db.init_app(app)
    # ３、集成redis
    global redis_store
    redis_store = StrictRedis(host=config[config_name].REDIS_HOST, port=config[config_name].REDIS_PORT, decode_responses=True)
    # ４、集成CSRFProtect
    @app.after_request
    def akter_request(response):
        csrf_token = generate_csrf()
        response.set_cookie("csrf_token", csrf_token)
        return response

    CSRFProtect(app)
    # 5、集成flask_session
    # 说明：flask中Session是用户保存用户数据的容器（上下文），而flask_session是指定session指定保存路径
    Session(app)

    # 添加过滤器
    app.add_template_filter(do_index_class, "index_class")

    # 为避免循环导入，注册蓝图，随时使用随时调用
    from info.modules.index import index_blu
    app.register_blueprint(index_blu)
    from info.modules.passport import passport_blu
    app.register_blueprint(passport_blu)

    return app