#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.db.models.loading import get_model
from django.db.models.query_utils import Q
from django.http import HttpResponseRedirect, HttpResponseForbidden
from annoying.widgets import AutocompleteTabularInline, AutocompleteModelAdmin
from recipients.forms import GroupRecipientForm
import settings
from sms_storage.forms import SMSForm
from sms_storage.models import SMS, SMSQueue, add_internal_sms_to_queue, SMSRecipientThrough, SMSRecipientGroupThrough

def changelist_add_to_queue(modeladmin, request, queryset):
    ids=u'all'
    if u'select_across' in request.POST:
        if request.POST['select_across']!=u'1':
            for id in request.POST.getlist(admin.ACTION_CHECKBOX_NAME):
                add_internal_sms_to_queue(id, request.user)

    ct = ContentType.objects.get_for_model(queryset.model)
    return HttpResponseRedirect("/admin/%s/%s/"%(ct.app_label, ct.model))

changelist_add_to_queue.short_description = u'Добавить в очередь'

class SMSAdmin(AutocompleteModelAdmin):
    model = SMS
    form = SMSForm
    exclude = ('sender', 'add_to_queue_count', 'creator')
    list_display = ('__unicode__','count_groups', 'count_recipients', 'add_to_queue_count','create_date', 'creator')
    list_filter = ('create_date',)
    list_select_related = True

    related_search_fields={
                'sms_recipient':                 ('search_name',),
                'sms_recipient_group':                 ( 'name',),
    }

    def save_model(self, request, obj, form, change):
        self.save_form(request, form, change)
        obj.sender = settings.SENDER
        if not change: #первое сохранение
            obj.creator = request.user

        obj.save()

        recipients = [t for t in form.cleaned_data['sms_recipient']]
        groups = [t for t in form.cleaned_data['sms_recipient_group']]

        obj.sms_recipient.clear()
        obj.sms_recipient_group.clear()
        for recipient in recipients:
            if not SMSRecipientThrough.objects.filter(recipient = recipient, sms=obj).count():
                m2 = SMSRecipientThrough.objects.create(recipient = recipient, sms=obj)
                m2.save()

        for group in groups:
            if not SMSRecipientGroupThrough.objects.filter(group = group, sms=obj).count():
                m2 = SMSRecipientGroupThrough.objects.create(group = group, sms=obj)
                m2.save()

        if 'add_to_queue' in form.cleaned_data and form.cleaned_data['add_to_queue']:
            send_to_queue=True
            sender_to_queue=request.user
        else:
            send_to_queue=False
            sender_to_queue=None
        obj.save(send_to_queue=send_to_queue, sender_to_queue=sender_to_queue)
    actions = [changelist_add_to_queue]

class SMSQueueAdmin(admin.ModelAdmin):
    model = SMSQueue
    search_fields = ('phone', 'text', )
    list_display = ('phone','changelist_text','changelist_status', 'queued_time','sent_time', 'changelist_sender', 'changelist_sms_id')
    list_filter = ('status','remote_sender')
    list_select_related = True
    raw_id_fields = ('internal_sms','internal_sender','remote_sender')

    def has_add_permission(self, request):
        return True if request.user.is_superuser else False

    def save_model(self, request, obj, form, change):
        if request.user.is_superuser:
            obj.save()
        else:
            pass

    def delete_model(self, request, obj):
        if request.user.is_superuser:
            obj.delete()
        else:
            pass

    def get_actions(self, request):
        actions = super(SMSQueueAdmin, self).get_actions(request)
        if not request.user.is_superuser:
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions
    
admin.site.register(SMS, SMSAdmin)
admin.site.register(SMSQueue, SMSQueueAdmin)
