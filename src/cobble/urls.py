from django.conf.urls import patterns, include, url
from django.contrib import admin

from reader.views import EntryListAPIView, ReaderView

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'cobble.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^api/v1/entry/$', EntryListAPIView.as_view(), name='entry-list'),

    url(r'^$', ReaderView.as_view(), name='reader'),
)
