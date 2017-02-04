#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.contrib import admin
from gateway.models import SMSGatewayUser

class SMSGatewayUserAdmin(admin.ModelAdmin):
    model = SMSGatewayUser
    exclude = ('creator',)
    list_display = ('__unicode__', 'max_message_len', 'creator','create_date')
    list_filter = ('create_date',)
    list_select_related = True

    def save_model(self, request, obj, form, change):
        obj.creator = request.user
        obj.save()

admin.site.register(SMSGatewayUser, SMSGatewayUserAdmin)
  