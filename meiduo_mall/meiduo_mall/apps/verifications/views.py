from django.shortcuts import render
from django.views import View
from django import http
from django_redis import get_redis_connection
from meiduo_mall.libs.captcha.captcha import captcha
from meiduo_mall.utils.response_code import RETCODE, err_msg
from random import randint
# from meiduo_mall.libs.yuntongxun.sms import CCP
from .constants import SMS_CODE_EXPIRE
from celery_tasks.sms.tasks import send_sms_code

import logging

# 创建日志输出器对象
logger = logging.getLogger('django')


class ImageCodeView(View):
    """图形验证码"""
    def get(self, request, uuid):

        # 1. 调用sdk 生成图形验证码
        # name: 唯一标识, text: 图形验证码字符串, image: 图形验证码图形bytes数据
        name, text, image = captcha.generate_captcha()

        # 2. 创建redis连接对象
        redis_conn = get_redis_connection('verify_codes')

        # 3. 将图形验证码 字符串存储到redis中
        redis_conn.setex(uuid, 300, text)

        # 4. 响应图片数据
        return http.HttpResponse(image, content_type='image/png')


class SMSCodeView(View):
    """短信验证码"""
    def get(self, request, mobile):
        # 2.1 创建redis连接对象
        redis_conn = get_redis_connection('verify_codes')
        # 先尝试获取redis中此手机号60s内是否发送短信标识
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        # 判断是否有标识,如果有提前响应
        if send_flag:
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '频繁发送短信'})

        # 1. 接收
        query_dict = request.GET
        image_code_client = query_dict.get('image_code')
        uuid = query_dict.get('uuid')
        # 判断是否有标识,如果有提前响应
        if send_flag:
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '频繁发送短信'})
        # 2. 校验
        if all([image_code_client, uuid]) is False:
            return http.HttpResponseForbidden('缺少必传参数')


        # 2.2 获取redis中图形验证码字符
        image_code_server_bytes = redis_conn.get(uuid)

        # 创建redis管道
        pl = redis_conn.pipeline()

        # 2.2.1 将redis中的图形验证码删除,让它是一次性（用完就删）
        # redis_conn.delete(uuid)
        pl.delete(uuid)
        # 2.3 判断redis中的图形验证码是否已过期
        if image_code_server_bytes is None:
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图形验证码已过期'})

        # 将bytes类型转换成str (从redis中获取出来的数据都是bytes  str, dict, list, set)
        image_code_server = image_code_server_bytes.decode()
        # 判断用户填写验证码和redis取的是否一致
        if image_code_client.lower() != image_code_server.lower():
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图形验证码填写错误'})

        # 3.发短信
        # 生成6位随机数字做为短信验证码
        sms_code = '%06d' % randint(0, 999999)
        logger.info(sms_code)

        # 3.1发送短信
        # CCP().send_template_sms('接收收短信手机号', ['验证码', '提示用户的过期时间:单秒分钟'], 1)
        send_sms_code.delay(mobile, sms_code)
        # 3.2 存储短信验证码到redis,以备注册时验证短信验证码
        # redis_conn.setex('sms_%s' % mobile, SMS_CODE_EXPIRE, sms_code)
        pl.setex('sms_%s' % mobile, SMS_CODE_EXPIRE, sms_code)
        # 3.3 向redis存储一个此手机号60s内发过短信标识
        # redis_conn.setex('send_flag_%s' % mobile, 60, 1)
        pl.setex('send_flag_%s' % mobile, 60, 1)

        # 执行管道
        pl.execute()

        # 4. 响应
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})


