from django.conf.urls import url, include
from . import views

urlpatterns = [

    url(r'^register',views.RegisterView.as_view(),name='register'),
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})',views.UsernameCountView.as_view(),name='count'),
    url(r'^login',views.LoginView.as_view(),name='login'),
    url(r'^userinfo',views.UserInfoView.as_view(),name='userinfo'),
    url(r'^emails',views.EmailView.as_view(),name='emails'),
    # url(r'^site',views.AddressView.as_view(),name='site'),

    url(r'^addresses/create',views.NewAddressView.as_view(),name='create'),
    url(r'^addresses/$',views.ShowAddressView.as_view(),name='show_addresses'),
    url(r'^addresses/(?P<address_id>\d+)/$',views.UqdateAddressView.as_view(),name='uqdate_addresses'),
    url(r'^addresses/(?P<address_id>\d+)/default/',views.DefAddressView.as_view(),name='def_addresses'),
    url(r'^addresses/(?P<address_id>\d+)/title/',views.UpdateTitleView.as_view(),name='uqdate_title'),
    url(r'^alterpassword/$',views.AlterPasswordView.as_view(),name='alter_password'),
    url(r'^browse_histories/',views.UserBrowseHistory.as_view(),name='browse_histories'),

]
