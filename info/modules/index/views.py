from . import index_blu
from info import redis_store

@index_blu.route("/")
def index():
    redis_store.set("age", "小邱")
    return "hello word"
