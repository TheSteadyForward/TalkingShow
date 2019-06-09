import random
import re
from info import constants
from flask import request, abort, current_app, make_response, jsonify
import json
from info import redis_store
from . import passport_blu
from info.utils.captcha.captcha import captcha
from info.utils.response_code import *
from info.libs.yuntongxun.sms import CCP


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
