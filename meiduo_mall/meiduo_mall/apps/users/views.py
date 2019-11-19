from django.shortcuts import render

from django.views import View
from django import http


class RegisterView(View):
    """注册"""
    def get(self, request):
        return render(request, 'register.html')
