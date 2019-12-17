from django.conf.urls import url, include
from . import views

urlpatterns = [

url(r'login12', views.QQUserView.as_view(),name='qquser')

]
