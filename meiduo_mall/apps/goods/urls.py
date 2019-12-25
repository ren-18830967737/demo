from django.conf.urls import url, include
from . import views

urlpatterns = [


    url(r'^list/(?P<category_id>\d+)/(?P<page_num>\d+)/',views.ListView.as_view(),name='list'),
    url(r'^hot/(?P<category_id>\d+)/',views.SalesView.as_view(),name='sales'),
    url(r'^detail/(?P<sku_id>\d+)/',views.DetailView.as_view(),name='detail'),
]
