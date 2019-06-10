from flask import render_template, redirect, current_app, send_file, session

from info import constants
from info.models import User, News, Category
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

    # 2、点击排行
    clicks_news = list()
    try:
        clicks_news = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS).all()
    except Exception as e:
        current_app.logger.error(e)

    news_li = [new.to_basic_dict() for new in clicks_news]

    # 3.实现新闻分类
    categorys_li = list()
    try:
        categorys_li = Category.query.all()
    except Exception as e:
        current_app.logger.error(e)


    category_li = [category.to_dict() for category in categorys_li]





    data = {
        "user_info": user.to_dict() if user else None,
        "news_li":news_li,
        "category_li":category_li
    }

    return render_template("news/index.html",
                           data=data,
                           )


@index_blu.route("/favicon.ico")
def favicon():
    # return redirect("/static/news/favicon.ico")
    # return current_app.send_static_file("news/favicon.ico")
    return send_file("static/news/favicon.ico")