from . import index_blu
from info import

@index_blu.route("/")
def index():
    return "hello word"
