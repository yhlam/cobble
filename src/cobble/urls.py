from django.conf.urls import patterns, include, url
from django.contrib import admin

from reader.views import (
    EntryListAPIView, UpdateReadAPIView, ReaderView, LoginView, LogoutView
)

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'cobble.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^api/v1/entry/$', EntryListAPIView.as_view(), name='entry-list'),

    url(r'^api/v1/entry/(?P<pk>\d+)/read/$', UpdateReadAPIView.as_view(read=True), name='entry-read'),
    url(r'^api/v1/entry/(?P<pk>\d+)/unread/$', UpdateReadAPIView.as_view(read=False), name='entry-unread'),

    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),

    url(r'^$', ReaderView.as_view(), name='reader'),
)
