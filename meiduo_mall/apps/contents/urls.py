from django.conf.urls import url, include
from . import views

urlpatterns = [


    url(r'^index',views.IndexView.as_view(),name='index')
]
