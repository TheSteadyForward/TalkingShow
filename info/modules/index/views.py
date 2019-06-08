from flask import render_template, redirect, current_app, send_file
from . import index_blu



@index_blu.route("/")
def index():
    return render_template("news/index.html")


@index_blu.route("/favicon.ico")
def favicon():
    # return redirect("/static/news/favicon.ico")
    # return current_app.send_static_file("news/favicon.ico")
    return send_file("static/news/favicon.ico")