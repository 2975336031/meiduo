from django.conf.urls import url

from . import views


urlpatterns = [
    # 拼接QQ登录url
    url(r'^qq/authorization/$', views.QQAuthURLView.as_view()),
    url(r'^oauth_callback/$', views.QQAuthView.as_view()),
]