from info import constants
from flask import request, abort, current_app, make_response
import json
from info import redis_store
from . import passport_blu
from info.utils.captcha.captcha import captcha



@passport_blu.route("/image_code")
def get_image_code():
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

    try:
        # 将验证码存入redis数据库
        redis_store.setex("IMG"+image_code, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)
    # response = make_response(image)
    # response.header
    return image
