from django.conf.urls import patterns, url

from .views import (
    EntryListAPIView,
    SetReadAPIView,
    SetUnreadAPIView,
    SetExpandedAPIView,
    SetOpenedAPIView,
    SetStarredAPIView,
    SetUnstarredAPIView,
    RetrieveUserConfigAPIView,
    FetchAPIView,
    DestoryReadEntryAPIView,
)


urls = patterns(
    '',
    url(r'^entry/$', EntryListAPIView.as_view(), name='entry-list'),

    url(r'^entry/(?P<pk>\d+)/read/$', SetReadAPIView.as_view(), name='entry-read'),
    url(r'^entry/(?P<pk>\d+)/unread/$', SetUnreadAPIView.as_view(), name='entry-unread'),
    url(r'^entry/(?P<pk>\d+)/expanded/$', SetExpandedAPIView.as_view(), name='entry-expanded'),
    url(r'^entry/(?P<pk>\d+)/opened/$', SetOpenedAPIView.as_view(), name='entry-opened'),
    url(r'^entry/(?P<pk>\d+)/star/$', SetStarredAPIView.as_view(), name='entry-star'),
    url(r'^entry/(?P<pk>\d+)/unstar/$', SetUnstarredAPIView.as_view(), name='entry-unstar'),

    url(r'^config/$', RetrieveUserConfigAPIView.as_view(), name='config'),

    url(r'^fetch/$', FetchAPIView.as_view(), name='fetch'),

    url(r'^entry/read/$', DestoryReadEntryAPIView.as_view(), name='entry-read-destory'),
)
