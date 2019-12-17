from django.conf.urls import url, include
from . import views

urlpatterns = [

    url(r'^register',views.RegisterView.as_view(),name='register'),
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})',views.UsernameCountView.as_view(),name='count'),
    url(r'^login',views.LoginView.as_view(),name='login'),
    url(r'^userinfo',views.UserInfoView.as_view(),name='userinfo'),
    url(r'^emails',views.EmailView.as_view(),name='emails'),
    url(r'^site',views.AddressView.as_view(),name='site'),

]
