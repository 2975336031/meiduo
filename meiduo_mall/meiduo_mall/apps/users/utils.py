from django.contrib.auth.backends import ModelBackend
import re
from .models import User


def get_user_by_account(account):
    """
    传入用户名或手机号,查询user
    :param account: username or mobile
    :return: user or None
    """
    try:
        if re.match(r'^1[3-9]\d{9}$', account):
            user = User.objects.get(mobile=account)
        else:
            user = User.objects.get(username=account)
        return user
    except User.DoesNotExist:
        return None


class UsernameMobileAuthBackend(ModelBackend):
    """自定义Django认证后端类"""
    def authenticate(self, request, username=None, password=None, **kwargs):

        # 1. 动态根据用户名或手机号查询user
        user = get_user_by_account(username)

        # 2. 校验密码是否正确
        if user and user.check_password(password):
            # 返回user or None
            return user
