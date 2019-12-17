from django.conf.urls import url, include
from . import views

urlpatterns = [


    url(r'^areas/',views.AddressView.as_view(),name='areas')
]
