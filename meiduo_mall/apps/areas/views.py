from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View
from django.core.cache import cache

from apps.areas.models import Area
from apps.users.models import User

from utils.response_code import RETCODE

"""
前端行为:用户点击省给后端发送请求
后端行为:根据前端请求的信息进行解析
   
        






"""

#省市区
class AddressView(View):
    def get(self,request):

        #获取请求
        parent_id = request.GET.get('area_id')

        #判断    parent_id不存在就是查找省的信息
        if parent_id is None:
            #设置缓存
            cache_pro = cache.get('cache_pro')
            if cache_pro is None:
                proviences  =Area.objects.filter(parent=None)
                cache_pro=[]
                #将对象转换成字典形式
                for pro in proviences:
                    cache_pro.append({
                        'id':pro.id,
                        'name':pro.name

                    })
                #设置缓存
                cache.set('cache_pro', cache_pro, 24*3600*14)

            return JsonResponse({'code':RETCODE.OK,'province_list':cache_pro})

        # parent_id存在就是查找市的信息
        else:
            #获取缓存
            city_list = cache.get('city_%s'%parent_id)
            if city_list is None:
                citys = Area.objects.filter(parent_id=parent_id)
                city_list = []
                #将对象转换成字典模式
                for city in citys:
                    city_list.append({
                        'id':city.id,
                        'name':city.name
                    })
                #设置缓存
                cache.set('city_%s'%parent_id,city_list, 24*3600*14)

            return  JsonResponse({'code':RETCODE.OK,'subs':city_list})

