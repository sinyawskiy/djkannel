#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.contrib import admin
from recipients.forms import GroupRecipientForm
from recipients.models import Recipient, GroupRecipient
from annoying.widgets import AutocompleteModelAdmin

class RecipientAdmin(admin.ModelAdmin):
    model = Recipient
    list_display = ('last_name', 'first_name', 'patronymic', 'male_sex', 'birth_date', 'phone')
    list_filter = ('male_sex', 'birth_date')
    exclude = ('search_name',)

class GroupRecipientAdmin(AutocompleteModelAdmin):
    form = GroupRecipientForm
    model = GroupRecipient
    list_display = ('name', 'count_recipients', 'max_message_len', 'description','id', 'password')
    list_select_related = True

    related_search_fields={
        'recipient': ('search_name',),
    }

    class Media:
        js = ('/media/js/edit_group_recipient_admin.js',)

admin.site.register(Recipient, RecipientAdmin)
admin.site.register(GroupRecipient, GroupRecipientAdmin)
  