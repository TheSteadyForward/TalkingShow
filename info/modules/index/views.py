from flask import render_template, redirect, current_app, send_file, session

from info.models import User
from . import index_blu



@index_blu.route("/")
def index():
    """
    1.获取session值
    2.通过session值查找是否存在
    3.传递参数
    :return:
    """
    user_id = session.get("user_id")

    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    data = {
        "user_info":user.to_dict() if user else None
    }

    return render_template("news/index.html",
                           data=data)


@index_blu.route("/favicon.ico")
def favicon():
    # return redirect("/static/news/favicon.ico")
    # return current_app.send_static_file("news/favicon.ico")
    return send_file("static/news/favicon.ico")