from libs.yuntongxun.sms import CCP
from celery_tasks.main import app

#设置生产者

@app.task()
def send_sms_code(mobile, sms_code):
    CCP().send_template_sms(mobile, [sms_code, 5], 1)



