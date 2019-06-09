import random
import re
import json
from info import constants, db
from flask import request, abort, current_app, make_response, jsonify, session
from info import redis_store
from info.models import User
from . import passport_blu
from info.utils.captcha.captcha import captcha
from info.utils.response_code import *
from info.libs.yuntongxun.sms import CCP
from werkzeug.security import check_password_hash
from datetime import datetime


@passport_blu.route("/login")
def login():
    """
    1.接收参数 mobile  passport
    2.校验参数
    3.mobile 查询数据库,判断是否存在
    4.校验 passport
    5.添加最后登录时间
    6.session状态保持
    7.返回前端响应
    :return:
    """
    # 1.接收参数
    dict_data = request.json

    mobile = dict_data.get("mobile")
    passport = dict_data.get("passport")

    # 2.校验整体参数
    if not all([mobile, passport]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 3.1 查询数据库，判断用户是否存在
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        return jsonify(errno=RET.DATAERR, errmsg="数据库查询失败")
    # 3.2 判断用户是否存在
    if not user:
        return jsonify(errno=RET.NODATA, errmsg="用户未注册")

    # 4.判断密码是否正确
    if not check_password_hash(passport):
        return jsonify(errno=RET.NODATA, errmsg="密码错误")

    # 5.添加登录时间
    User.last_login = datetime.now()
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DATAERR, errmsg="数据保存失败")

    # 6.session状态保持
    session["user_id"] = user.id

    # 7.返回前端响应
    return jsonify(errno=RET.OK, errmsg="数据保存成功")


@passport_blu.route("/register", methods=["POST"])
def refister():
    """注册提交"""
    """
    1、获取mobile  smscode  password
    2、整体进行校验
    3、mobile 正则
    4、smscode  进行验证
    5、初始化User对象
    6、核心添加数据库信息
    7、session保持状态
    8、响应前端
    :return:
    """
    dict_data = request.json

    mobile = dict_data.get("mobile")
    smscode = dict_data.get("smscode")
    password = dict_data.get("password")

    # 1.整体校验
    if not all([mobile, smscode, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 2.mobile手机号 正则校验
    if not re.match(r"1[3456789]\d{9}", mobile):
        return jsonify(errno=RET.DATAERR, errmsg="手机号输入错误")
    try:
        redis_sms = redis_store.get(mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询失败")

    # 3.判断数据查询是否存
    if not redis_sms:
        return jsonify(errno=RET.NODATA, errmsg="短信验证码已经过期")

    # 4.短信验证码进行校验
    if redis_sms != smscode:
        return jsonify(errno=RET.DATAERR,errmsg="用户输入短信验证码错误")

    # 5.初始化User对象，将用户信息添加数据库
    user = User()
    user.nick_name = mobile
    user.password = password
    user.mobile = mobile
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="数据保存失败")

    # 6.session保持状态
    session["user_id"] = user.id

    # 7.返回前端响应
    return jsonify(errno=RET.OK, errmsg="注册成功")


@passport_blu.route("/sms_code", methods=["POST"])
def get_sms_code():

    """点击获得手机验证码"""
    """
    1、获取参数 mobile image_code image_code_id
    2、整体校验
    3、校验 mobile 正则
    4、校验image_code，用户输入验证码
    5、校验 image_code_id  从redis数据库取出验证码与之校验
    6、生成六位验证吗
    7、接收信息是否发送成功
    :return:
    """
    # data_json = request.data.deconde()
    # dict_data = json.loads(data_json)
    dict_data = request.json
    # 1、获取参数 mobile image_code image_code_id
    mobile = dict_data.get("mobile")
    image_code = dict_data.get("image_code")
    image_code_id = dict_data.get("image_code_id")

    # 2、整体校验
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    # 3、校验mobile
    if not re.match(r"1[3456789]\d{9}", mobile):
        return jsonify(errno=RET.DATAERR, errmsg="手机号输入错误")
    # 4、从redis数据库中查询数据
    try:
        real_image_code = redis_store.get("IMG"+image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="数据库查询错误")
    # 判断redis数据库数据是否已经过期
    if not real_image_code:
        return jsonify(errno=RET.NODATA, errmsg="图片验证码已经过期")
    # 校验用户输入数据与redis存储数据是否一致
    if image_code.upper() != real_image_code.upper():
        return jsonify(errno=RET.DATAERR, errmsg="图片验证码填写错误")

    sms_code = "%06d" % random.randint(0, 999999)
    # ccp = CCP()
    # result = ccp.send_template_sms(mobile, [sms_code, 5], 1)
    #
    # if result != 0:
    #     return jsonify(errno=RET.OK, errmsg="短信发送失败")
    current_app.logger.info("手机验证码是%s" % sms_code)
    try:
        redis_store.setex(mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="数据储存失败")

    return jsonify(errno=RET.OK, errmsg="短信发送成功")



@passport_blu.route("/image_code")
def get_image_code():
    """获取图片验证码"""
    """
    1、获取UUid
    2、判断是否存在，如果不在则报错
    3、获取验证码图片和文本
    4、将获取验证码储存在redis数据库中
    5、返回前端响应
    :return:
    """
    # 1、获取前端传入的参数
    image_code = request.args.get("imagecode")
    # 2、判断获取数据是否存在
    if not image_code:
        abort(404)

    # 使用工具包生成验证码文本和验证码图片
    _, text, image = captcha.generate_captcha()
    current_app.logger.info("图片验证码是%s" % text)

    try:
        # 将验证码存入redis数据库
        redis_store.setex("IMG"+image_code, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)
    # response = make_response(image)
    # response.header
    return image
