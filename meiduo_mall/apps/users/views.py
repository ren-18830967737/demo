import json

import re
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.views import View

from utils.response_code import RETCODE
from .models import User
import logging
logger = logging.getLogger('django')
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
        user = User.objects.create_user(username=username, password=password, mobile=mobile)
        #状态保持
        from django.contrib.auth import login
        login(requset, user)
        #返回响应
        response = redirect('/index.html')
        response.set_cookie('username', user.username, max_age=24*3600*14)
        return response
#用户名是否重复
class UsernameCountView(View):


    def get(self,request, username):
        #查看用户的数量
        count = User.objects.filter(username=username).count()
        return JsonResponse({'code':'ok', 'errmsg':'ok', 'count':count})



#用户登录
class LoginView(View):


    def get(self,request):

        return render(request, 'login.html')

    def post(self,request):


        #获取用户
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        remembered = request.POST.get('remembered')
        #验证字

        if not all([username, password]):
            return HttpResponseBadRequest('参数不全')
        #django自带认证

        from django.contrib.auth import authenticate

        user = authenticate(username=username, password=password)

        if user is None:
            return HttpResponseBadRequest('用户名或密码错误')

        #状态保持
        from django.contrib.auth import login
        login(request,user)
        #是否保存用户名
        if remembered != 'on':
            request.session.set_expiry(0)
        else:
            request.session.set_expiry(None)

        #返回响应
        response = redirect('index.html')
        #设置cookie
        response.set_cookie('username',user.username, max_age=24*3600*14)

        return response




#个人中心页面
class UserInfoView(View):


    def get(self,requset):
        #获取用户名 手机号 邮箱
        data = {
            'username':requset.user.username,
            'mobile':requset.user.mobile,
            'email':requset.user.email,
            'email_active':requset.user.email_active
        }
        #返回响应


        return render(requset, 'user_center_info.html', context=data)

#添加邮箱
class EmailView(View):
    def put(self,request):

        #获取邮箱

        json_str = request.body.decode()
        data = json.loads(json_str)
        email = data.get('email')

        #验证数据
        if not email:
            return HttpResponseBadRequest('请写入邮箱')
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return HttpResponseBadRequest('参数email有误')

        try:
            request.user.email=email
            request.user.save()
        except Exception as e:
            logger.error(e)
            return HttpResponseBadRequest('添加邮箱失败')
        return JsonResponse({'code':RETCODE.OK, 'errmsg':'添加邮箱成功'})



#收货地址
class AddressView(View):
    def get(self,request):
        return render(request, 'user_center_site.html')









