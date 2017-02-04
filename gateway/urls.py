#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from gateway.views import UserGateway, KannelGateway, UserGatewayToGroup

urlpatterns = patterns('',
    url(r'^sendsms/', UserGateway.as_view(), name='user_gateway'),
    url(r'^sendsmstogroup/', UserGatewayToGroup.as_view(), name='user_gateway_to_group'),
    url(r'^smsstatus/', KannelGateway.as_view(), name='kannel_gateway'),
)
  