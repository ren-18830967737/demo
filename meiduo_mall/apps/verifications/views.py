from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View
from libs.captcha.captcha import captcha
from django_redis import get_redis_connection


#图片验证码
class ImageCodeView(View):
    """
    获取uuid
    生成验证码
    连接redis
    保存
    返回响应
    
    
    """
    def get(self,request, uuid):

        #获取uuid
        #生成验证


        # text 就是生成的图片验证码的内容,例如 abcd
        # image 就是 图片二进制
        text, image = captcha.generate_captcha()
        #连接redis
        from django_redis import get_redis_connection
        redis_conn = get_redis_connection('code')
        #保存
        redis_conn.setex('img_%s'% uuid, 120, text)
        # 返回响应
        return HttpResponse(image, content_type='image/jpeg')



#手机验证码
class SmsCodes(View):

    def get(self,request, mobile):

        #获取数据 uuid 图形验证码

        uuid = request.GET.get('image_code_id')

        image_code = request.GET.get('image_code')

        #验证数据
        if not all([mobile, uuid, image_code]):
            return HttpResponseBadRequest('参数不全')

        #连接数据库
        redis_conn = get_redis_connection('code')

        #获取redis 中的验证码
        image_code_redis = redis_conn.get('img_%s' %uuid)

        if image_code_redis is None:
            return HttpResponseBadRequest('验证码过期')

        image_code_redis1 = image_code_redis.decode()
        #跟redis中的验证码进行对比
        if image_code.lower() != image_code_redis1.lower():
            return HttpResponseBadRequest('验证码输入错误')
        #查询手机号在短时间内是否频繁
        send_flag = redis_conn.get('send_flag_%s' %mobile)
        if send_flag:
            return JsonResponse({'code': 4001, 'errmsg': '发送短信过于频繁'})



        #生成验证码
        from random import randint
        sms_code = '%06d' % randint(0, 999999)
        # 保存到数据库
        redis_conn.setex('sms_%s' %mobile, 60, sms_code)

        #发送短信
        # from libs.yuntongxun.sms import CCP
        # CCP().send_template_sms(mobile, [sms_code, 5], 1)


        from celery_tasks.sms.tasks import send_sms_code

        send_sms_code.delay(mobile, sms_code)
        # send_sms_code.delay(self, sms_code)
        # 设置手机号使用次数
        redis_conn.setex('send_flag_%s' % mobile, 60, 1)

        #返回响应
        return JsonResponse({'msg': 'ok', 'code': '0'})









