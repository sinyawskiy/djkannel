#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from annoying.russian_admin import admin
from django.views.generic.base import RedirectView

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin_tools/', include('admin_tools.urls')),
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^$', RedirectView.as_view(url='/admin/'), name='main_redirect'),
    (r'^gateway/', include('gateway.urls')),
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
