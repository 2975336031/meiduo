from django.shortcuts import render
from django.views import View
from django import http
from django_redis import get_redis_connection
from meiduo_mall.libs.captcha.captcha import captcha


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

