from django.shortcuts import render

from django.views import View
from django import http
import re
from .models import User
from django.contrib.auth import login, authenticate
from django_redis import get_redis_connection


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
        # 短信验证码的验证代码后期补充
        # 创建redis连接
        redis_conn = get_redis_connection('verify_codes')
        # 获取redis的当前手机号对应的短信验证码
        sms_code_server = redis_conn.get('sms_%s' % mobile)
        # 将获取出来的短信验证码从redis删除(让短信验证码是一次性)
        redis_conn.delete('sms_%s' % mobile)
        # 判断短信验证码是否过期
        if sms_code_server is None:
            return render(request, 'register.html', {'register_errmsg': '短信验证码已过期'})
        # 判断用户填写短信验证码是否正确
        if sms_code != sms_code_server.decode():
            return render(request, 'register.html', {'register_errmsg': '短信验证码填写错误'})

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


class LoginView(View):
    """用户登录"""

    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        """用户登录"""
        # 1. 接收
        query_dict = request.POST
        username = query_dict.get('username')
        password = query_dict.get('password')
        remembered = query_dict.get('remembered')

        # 2. 校验
        if all([username, password]) is False:
            return http.HttpResponseForbidden('缺少必传参数')

        # 3. 判断用户名及密码是否正确
        user = authenticate(request, username=username, password=password)
        if user is None:
            return http.HttpResponseForbidden('用户名或密码错误')

        # 4. 状态保持
        login(request, user)

        if remembered is None:  # 如果用户没有勾选记住登录,设置session过期时间为会话结束
            request.session.set_expiry(0)

        # 5. 重定向
        return http.HttpResponse('跳转到首页')