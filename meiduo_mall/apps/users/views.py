import json

import re
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.views import View

from .models import User

"""
需求分析
    post请求
    获取数据
    验证数据
    保存到数据库
    返回响应

"""
#用户注册
class RegisterView(View):

    def get(self, request):
        return render (request, 'register.html')

    def post(self,requset):
        #获取数据

        username = requset.POST.get('username')
        password = requset.POST.get('password')
        password2 = requset.POST.get('password2')
        mobile = requset.POST.get('mobile')
        allow = requset.POST.get('allow')


        #验证数据
        if not all([username, password,password2, mobile, allow]):
            return HttpResponseBadRequest('缺少参数')
        if not re.match(r'^[a-zA-Z0-9_]{5,20}$', username):
            return HttpResponseBadRequest('用户名错误')
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return HttpResponseBadRequest('密码错误')
        if  password != password2:
            return HttpResponseBadRequest('两次输入密码不一致')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseBadRequest('手机号格式不对')
        if allow != 'on':
            return HttpResponseBadRequest('请勾选用户协议')

        #保存数据
        user = User.objects.create(username=username, password=password, mobile=mobile)
        #状态保持
        from django.contrib.auth import login
        login(requset, user)
        #返回响应
        return redirect('/index.html')

#用户名是否重复
class UsernameCountView(View):


    def get(self,request, username):
        #查看用户的数量
        count = User.objects.filter(username=username).count()
        return JsonResponse({'code':'ok', 'errmsg':'ok', 'count':count})