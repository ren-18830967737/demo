import json

import re
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views import View
from django_redis import get_redis_connection

from apps.goods.models import SKU
from utils.response_code import RETCODE
from .models import User, Address
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







#新增收货地址
class NewAddressView(View):


    def post(self, request):
        #验证数据

        address_count =  request.user.addresses.count()
        if address_count > 20:
            return JsonResponse({'code':RETCODE.THROTTLINGERR,'errmsg':'地址数量上限'})

        #获取数据
        data = json.loads(request.body.decode())
        receiver = data.get('receiver')
        province_id = data.get('province_id')
        city_id = data.get('city_id')
        district_id = data.get('district_id')
        place = data.get('place')
        mobile = data.get('mobile')
        tel = data.get('tel')
        email = data.get('email')
        # 验证参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return HttpResponseBadRequest('缺少参数')

        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseBadRequest('参数mobile有误')

        #保存到数据库
        try:

            address = Address.objects.create(


                user=request.user,
                title = receiver,
                receiver=receiver,
                province_id = province_id,
                city_id = city_id,
                district_id = city_id,
                place = place,
                mobile = mobile,
                tel = tel,
                email = email

            )
            if not request.user.default_address:
                request.user.default_address = address
                request.user.save()
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg':'保存地址失败'})
        #地址新增成功 实现局部刷新
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }
        return JsonResponse({'code':RETCODE.OK,
                             'errmsg':'新增地址成功',
                             'address':address_dict
                             })






#获取地址列表
class ShowAddressView(View):
    def get(self,request):
        # 获取当前用户
        login_user= request.user
        addresses = Address.objects.filter(user=login_user, is_deleted=False)

        address_list=[]
        for address in addresses:
            address_dict={
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "province_id": address.province_id,
                "city": address.city.name,
                "city_id": address.city_id,
                "district": address.district.name,
                "district_id": address.district_id,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            }
            address_list.append(address_dict)
        context = {
            'default_address_id': login_user.default_address_id,
            'addresses': address_list,
        }

        return render(request, 'user_center_site.html', context)




#修改地址和删除地址
class UqdateAddressView(View):


    def put(self,request, address_id):

        #获取数据
        data_str = request.body.decode()
        data = json.loads(data_str)
        receiver = data.get('receiver')
        province_id = data.get('province_id')
        city_id = data.get('city_id')
        district_id = data.get('district_id')
        place = data.get('place')
        mobile = data.get('mobile')
        tel = data.get('tel')
        email = data.get('email')

        #验证数据
        if not all([address_id, receiver, province_id, city_id, district_id,place, mobile]):
            return HttpResponseBadRequest('缺少信息')

        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseBadRequest('参数mobile有误')

        #判断地址是否存在
        try:
            Address.objects.filter(id=address_id).update(
                user = request.user,
                title = receiver,
                receiver = receiver,
                province_id = province_id,
                city_id = city_id,
                district_id = district_id,
                place = place,
                mobile = mobile,
                tel = tel,
                email = email
            )

        except Exception as e:
            logger.error(e)
            return JsonResponse({'code':RETCODE.DBERR,'errmsg':'更新地址失败'})

        #保存到数据库
        address  = Address.objects.get(id=address_id)
        address_dict = {
            'id':address.id,
            'title':address.receiver,
            'receiver':address.receiver,
            'province':address.province.name,
            'city':address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }
        #返回响应
        return JsonResponse({
            'code':RETCODE.OK,
            'errmsg':'更新地址成功',
            'address':address_dict
        })

    #删除地址
    def delete(self,request, address_id):



        try:
            #获取地址
            address = Address.objects.get(id=address_id)
            #逻辑删除
            address.is_deleted = True
            address.save()
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code':RETCODE.DBERR, 'errmsg':'删除地址失败'})

        #返回响应
        return JsonResponse({'code':RETCODE.OK, 'errmsg':'删除地址成功'})

#设置默认地址
class DefAddressView(View):

    def put(self,request, address_id):
        #获取地址

        #更新数据库
        try:
            address = Address.objects.get(id=address_id)
            request.user.default_address = address
            request.user.save()
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code':RETCODE.DBERR, 'errmsg':'设置默认地址失败'})

        return JsonResponse({'code':RETCODE.OK, 'errmsg':'默认地址设置成功'})






#修改地址标题
class UpdateTitleView(View):

    def put(self,request,address_id):
        #获取数据
        data_str = request.body.decode()
        data = json.loads(data_str)
        title = data.get('title')
        #获取该地址
        address = Address.objects.get(id=address_id)

        try:
            address.title = title
            address.save()
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code':RETCODE.DBERR, 'errmsg':'标题修改失败'})

        return JsonResponse({'code':RETCODE.OK, 'errmsg':'标题修改成功'})








#修改密码
class AlterPasswordView(View):
    def get(self,request):
        return render(request, 'user_center_pass.html')


    def post(self,request):

        #接收数据
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        new_password2 = request.POST.get('new_password2')

        #验证数据
        if not all([old_password, new_password, new_password2]):
            return HttpResponseBadRequest('缺少必传参数')
        if not re.match(r'^[0-9A-Za-z]{8,20}$', new_password):
            return HttpResponseBadRequest('密码最少8位，最长20位')
        if new_password != new_password2:
            return HttpResponseBadRequest('两次输入的密码不一致')

        if not request.user.check_password(old_password):
            return render(request, 'user_center_pass.html',
                          {'origin_password_errmsg': '原始密码错误'})
        #保存到数据库
        try:
            request.user.set_password(new_password)
            request.user.save()

        except Exception as e:
            logger.error(e)
            return render(request, 'user_center_pass.html',
                          {'change_password_errmsg': '修改密码失败'})

        response = redirect(reverse('users:login'))
        response.delete_cookie('username')
        return response




#用户游览记录
class UserBrowseHistory(View):


    def post(self,request):
        #获取数据
        data_str = request.body.decode()
        data = json.loads(data_str)
        sku_id = data.get('sku_id')

        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return HttpResponseBadRequest('sku商品不存在')
        #连接redis
        conn_redis = get_redis_connection('history')
        user_id = request.user.id

        #创建管道实例
        pipeline = conn_redis.pipeline()
        #移除
        pipeline.lrem('history_%s' %request.user.id, 0,sku_id)
        #从左添加
        pipeline.lpush('history_%s' %request.user.id, sku_id)
        #只保存5个数据
        pipeline.ltrim('history_%s' %request.user.id, 0, 4)
        pipeline.execute()
        return JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok'})
    def get(self,request):

        #读取数据
        conn_redis = get_redis_connection('history')
        sku_ids = conn_redis.lrange('history_%s' %request.user.id,0, -1)

        sku_list = []
        for sku_id in sku_ids:
            sku = SKU.objects.get(id=sku_id)
            sku_list.append({
                'id': sku.id,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': sku.price
            })




        return JsonResponse({'code':RETCODE.OK, 'errmsg':'OK','skus':sku_list})
















