from django.conf.urls import patterns, include, url
from django.contrib import admin

from reader.views import ReaderView, LoginView, LogoutView, StatExportView
from reader import api as reader_api

urlpatterns = patterns(
    '',
    # Examples:
    # url(r'^$', 'cobble.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^api/v1/', include(reader_api.urls)),

    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),

    url(r'stat/$', StatExportView.as_view(), name='stat'),

    url(r'^$', ReaderView.as_view(), name='reader'),
)
