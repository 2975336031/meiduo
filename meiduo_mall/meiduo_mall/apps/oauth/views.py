from django.views import View
from QQLoginTool.QQtool import OAuthQQ
from django import http

from meiduo_mall.utils.response_code import RETCODE
from django.conf import settings


class QQAuthURLView(View):
    """拼接QQ登录url"""
    def get(self, request):
        # 1. 接收查询参数
        next = request.GET.get('next') or '/'

        # 2. 创建OAuthQQ 对象
        # auth_tool = OAuthQQ(client_id='appid', client_secret='appkey', redirect_uri='回调地址', state='把它当成next')
        # auth_tool = OAuthQQ(client_id='101568493', client_secret='e85ad1fa847b5b79d07e40f8f876b211', redirect_uri='http://www.meiduo.site:8000/oauth_callback', state=next)
        auth_tool = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                            client_secret=settings.QQ_CLIENT_SECRET,
                            redirect_uri=settings.QQ_REDIRECT_URI,
                            state=next)

        # 3. 调用OAuthQQ 里面的get_qq_url方法得到拼接好的QQ登录url
        login_url = auth_tool.get_qq_url()

        # 4. 响应json
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'login_url': login_url})


class QQAuthView(View):
    """QQ登录成功回调处理"""
    def get(self, request):
        # 1. 获取查询参数中的code
        code = request.GET.get('code')
        # 2. 校验
        if code is None:
            return http.HttpResponseForbidden('缺少code')
        # 3. 创建QQ登录工具对象
        auth_tool = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                            client_secret=settings.QQ_CLIENT_SECRET,
                            redirect_uri=settings.QQ_REDIRECT_URI)

        # 4. 调用get_access_token
        access_token = auth_tool.get_access_token(code)
        #  调用get_openid
        openid = auth_tool.get_open_id(access_token)
        # 查询openid是否和美多中的user有关联
        pass
