"""
1、集成配置类
2、集成sqlalchemy     pip install flask_sqlalchemy
3、集成redis          pip install flask_redis
4、集成CRSFProtect    pip install falsk_wtf
5、集成flask_session  pip install flask_session
6、集成falsk_script   pip install falsk_script
7、集成flask_migrate  pip install falsk_migrate
"""
import logging
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from info import set_config,db


app = set_config("develop")
# 6、集成falsk_manager
manager = Manager(app)
# 7、集成flask_migrate
Migrate(app, db)
manager.add_command("db", MigrateCommand)


@app.route("/")
def index():
    logging.debug("debug")
    logging.info("info")
    logging.warning("waring")
    logging.error("error")
    logging.fatal("fatal")
    return "hello word"


if __name__ == '__main__':
    manager.run()