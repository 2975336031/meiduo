from django.shortcuts import render

from django.views import View
from django import http
import re
from .models import User
from django.contrib.auth import login


class RegisterView(View):
    """注册"""
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        # 1.接收请求体中的表单数据  POST
        query_dict = request.POST
        username = query_dict.get('username')
        password = query_dict.get('password')
        password2 = query_dict.get('password2')
        mobile = query_dict.get('mobile')
        sms_code = query_dict.get('sms_code')
        allow = query_dict.get('allow')  # None,   'on'

        # 2.校验
        if all([username, password, password2, mobile, sms_code, allow]) is False:
            return http.HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden('请输入5-20个字符的用户')
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('请输入8-20个字符的密码')
        if password != password2:
            return http.HttpResponseForbidden('两次密码不一一致')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('请输入正确的手机号')
        # TODO: 短信验证码的验证代码后期补充

        # 3.新增用户
        user = User.objects.create_user(username=username, password=password, mobile=mobile)

        # 3.1 状态保持(保存住用户登录状态)
        login(request, user)

        # 4.响应
        return http.HttpResponse('注册成功即代表登录成功,重定向到首页')


class UsernameCountView(View):
    """判断用户名是否重复注册"""
    def get(self, request, username):
        # 校验
        count = User.objects.filter(username=username).count()
        # 响应json
        return http.JsonResponse({'count': count})


class MobileCountView(View):
    """判断手机号是否重复注册"""
    def get(self, request, mobile):
        # 校验
        count = User.objects.filter(mobile=mobile).count()
        # 响应json
        return http.JsonResponse({'count': count})