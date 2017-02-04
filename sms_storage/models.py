#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import os
from django.contrib.auth.models import User
from django.db import models
from django.db.models.query_utils import Q
from django.db.models.signals import post_save, m2m_changed
from django.dispatch.dispatcher import Signal
from recipients.models import phone_validator, GroupRecipient, Recipient, RecipientThrough
from gateway.models import SMSGatewayUser
import settings

class Property(property):
    pass

    #add_internal_sms_to_queue(self.id, sender_to_queue)

class SMS(models.Model):
    text = models.TextField(u'Текст сообщения')
    sender = models.CharField(u'Отправитель',max_length=32, default=settings.SENDER, blank=True)
    sms_recipient_group = models.ManyToManyField(GroupRecipient, verbose_name=u'группа', through='SMSRecipientGroupThrough', related_name='sms_recipient_group', blank=True)
    sms_recipient = models.ManyToManyField(Recipient, verbose_name=u'получатель', through='SMSRecipientThrough', related_name='sms_recipient', blank=True)
    create_date = models.DateTimeField(auto_now_add=True, verbose_name=u'дата и время создания')
    creator = models.ForeignKey(User, verbose_name=u'создатель', related_name='sms_creator_with_auth_user', null=True, blank=True)
    add_to_queue_count = models.IntegerField(u'поставлено в очередь раз', null=True, blank=True)
    
    def save(self, send_to_queue = False, sender_to_queue=None, *args, **kwargs):
        super(SMS, self).save(*args, **kwargs)
        if send_to_queue:
            add_internal_sms_to_queue(self.id, sender_to_queue)

    class Meta:
        ordering = ['create_date']
        verbose_name = u'СМС'
        verbose_name_plural = u'СМС сообщения'

    def __unicode__(self):
        return u'%d %s...' % (self.id, self.text[:20] if len(self.text) > 20 else self.text)

    def get_count_groups(self):
        sum_count = 0
        for group_item in SMSRecipientGroupThrough.objects.filter(sms_id=self.id):
            sum_count+=RecipientThrough.objects.filter(group_id = group_item.group_id).count()
        return u'%d (%d)' %(SMSRecipientGroupThrough.objects.filter(sms=self.id).count(), sum_count)
    count_groups= Property(get_count_groups)
    count_groups.short_description = u'Кол-во групп'

    def get_count_recipients(self):
        return SMSRecipientThrough.objects.filter(sms=self.id).count()
    count_recipients= Property(get_count_recipients)
    count_recipients.short_description = u'Кол-во получателей'

    def send_sms(self):
        pass

class SMSRecipientGroupThrough(models.Model):
    sms   = models.ForeignKey(SMS, verbose_name=u'sms', related_name='with_sms_recipient_group_trough')
    group = models.ForeignKey(GroupRecipient, verbose_name=u'группа', related_name='with_sms_recipient_group')

    class Meta:
        ordering = ['id']
        verbose_name = u'связь группа получатель'
        verbose_name_plural = u'получатели по группам'

class SMSRecipientThrough(models.Model):
    sms   = models.ForeignKey(SMS, verbose_name=u'sms', related_name='with_sms_recipient_trough')
    recipient   = models.ForeignKey(Recipient, verbose_name=u'получатель', related_name='with_sms_recipient')

    class Meta:
        ordering = ['id']
        verbose_name = u'связь группа получатель'
        verbose_name_plural = u'получатели по группам'

#Статусы заявок
class SMSStatus(object):
    QUEUED = 1  # Message local queued.
    CANCELED = 2  # Message was canceled before sending
    SENT = 3  # Message is sent ok, but status unknown.
    UNSENT = 4  # Message was not sent, and never will be.
    UNKNOWN = 5  # Message status is unknown
    REMOTE_QUEUED = 6  # Message queued on remote server
    DELIVERED = 7  # Message delivered to recipient
    UNDELIVERED = 8  # Message undelivered to recipient
    EXPIRED = 9  # Message was sent, but requesting status expired
    SMSC_SUBMIT = 10
    SMSC_REJECT = 11

    @classmethod
    def choices(cls):
        return ((cls.QUEUED, cls.type_to_name(cls.QUEUED)),
                (cls.CANCELED, cls.type_to_name(cls.CANCELED)),
                (cls.SENT, cls.type_to_name(cls.SENT)),
                (cls.UNSENT, cls.type_to_name(cls.UNSENT)),
                (cls.UNKNOWN, cls.type_to_name(cls.UNKNOWN)),
                (cls.REMOTE_QUEUED, cls.type_to_name(cls.REMOTE_QUEUED)),
                (cls.DELIVERED, cls.type_to_name(cls.DELIVERED)),
                (cls.EXPIRED, cls.type_to_name(cls.EXPIRED)),
                (cls.SMSC_SUBMIT, cls.type_to_name(cls.SMSC_SUBMIT)),
                (cls.SMSC_REJECT, cls.type_to_name(cls.SMSC_REJECT)))

    @classmethod
    def type_to_name(cls, type):
        if type == cls.QUEUED:
            return u'Добавлено в очередь'
        elif type == cls.CANCELED:
            return u'Отменено до отправки'
        elif type == cls.SENT:
            return u'Отправлено'
        elif type == cls.UNSENT:
            return u'Неотправлено'
        elif type == cls.UNKNOWN:
            return u'Неизвестно'
        elif type == cls.REMOTE_QUEUED:
            return u'Удаленно буферизировано'
        elif type == cls.DELIVERED:
            return u'Доставлено'
        elif type == cls.UNDELIVERED:
            return u'Недоставлено'
        elif type == cls.EXPIRED:
            return u'Отправлено и просрочено'
        elif type == cls.SMSC_SUBMIT:
            return u'Подтверждено'
        elif type == cls.SMSC_REJECT:
            return u'Отклонено'
        return u'неизвестный'

    @classmethod
    def type_to_color(cls, type):
        if type == cls.QUEUED:
            return u'blue'
        elif type == cls.CANCELED:
            return u'red'
        elif type == cls.SENT:
            return u'yellow'
        elif type == cls.UNSENT:
            return u'red'
        elif type == cls.UNKNOWN:
            return u'red'
        elif type == cls.REMOTE_QUEUED:
            return u'blue'
        elif type == cls.DELIVERED:
            return u'green'
        elif type == cls.UNDELIVERED:
            return u'red'
        elif type == cls.EXPIRED:
            return u'red'
        elif type == cls.SMSC_SUBMIT:
            return u'yellow'
        elif type == cls.SMSC_REJECT:
            return u'red'
        return u'red'

class SMSQueue(models.Model):
    '''
    This class describes each recipient of SMS, and actually works with SMS
    statuses, so class Sms only stores the message body and sender.
    '''

    phone = models.CharField(u'телефонный номер', max_length=11, validators=[phone_validator,],)
    remote_id = models.CharField(u'идентификатор', max_length=32, editable=False,)
    status = models.SmallIntegerField(u'статус', choices=SMSStatus.choices(), default=SMSStatus.QUEUED)
    queued_time = models.DateTimeField(u'время добавления', auto_now_add=True, editable=False,)
    status_time = models.DateTimeField(u'статус изменен', null=True, blank=True, editable=False,)
    sent_time = models.DateTimeField('время отправки', null=True, blank=True, editable=False,)
    status_text = models.CharField(u'текст статуса', max_length=64, null=True, blank=True, editable=False,)
    remote_sender = models.ForeignKey(SMSGatewayUser, verbose_name=u'пользователь шлюза', related_name='with_sms_recipient_group', blank=True, null=True)
    internal_sender = models.ForeignKey(User, verbose_name=u'внутренний отправитель', related_name='with_auth_user', blank=True, null=True)
    internal_sms = models.ForeignKey(SMS, verbose_name=u'внутренний список', related_name='with_internal_sms', blank=True, null=True)
    text = models.TextField(u'текст сообщения')
    delivery_url = models.URLField(u'url доставки', blank=True)

    def changelist_sms_id(self):
        return self.internal_sms_id if self.internal_sms else self.remote_id
    changelist_sms_id.short_description = u'СМС идент.'

    def changelist_sender(self):
        return u'%s (внутр.)' % self.internal_sender if self.internal_sender else u'%s (внешн.)'% self.remote_sender
    changelist_sender.short_description = u'отправитель'

    def changelist_status(self):
        return u'<span style="color: %s;">%s</span>' % (SMSStatus.type_to_color(self.status), SMSStatus.type_to_name(self.status))
    changelist_status.short_description = u'Статус'
    changelist_status.allow_tags = True
    changelist_status.admin_order_field = 'status'

    def changelist_text(self):
        return u'%s...' % self.text[:20] if len(self.text) > 20 else self.text
    changelist_text.short_description = u'Сообщение'

    class Meta:
        verbose_name = u'СМС из очереди'
        verbose_name_plural = u'СМС очередь'
        unique_together = (('phone', 'remote_id'),)
        ordering = (('-queued_time'),)

    def __unicode__(self):
        return u'%s(%s)' % (self.phone, SMSStatus.type_to_name(self.status))

def uniquer(old_list):
    b = []
    for i in old_list:
        description = u''
        for k in old_list:
            if k[0] == i[0]:
                if len(k[1]):
                    description = u'%s\n%s'%(description,k[1])
        exist = False
        for m in b:
            if m[1] == description and m[0] == i[0]:
                exist = True
        if not exist:
            b.append([i[0], description])
    return b

def add_remote_sms_to_queue(phone, text, delivery_url, gateway_user):

    remote_id_temp=u''
    while True:
        remote_id_temp = u'%s' % os.urandom(16).encode('hex')
        sms_queue_count = SMSQueue.objects.filter(Q(remote_id = remote_id_temp)).count()
        if not sms_queue_count:
            break

    sms_queue = SMSQueue()
    sms_queue.phone = phone
    sms_queue.remote_id = remote_id_temp
    sms_queue.delivery_url = delivery_url
    sms_queue.remote_sender = gateway_user
    sms_queue.text = text
    sms_queue.save()

def add_internal_sms_to_queue(id, internal_sender):
    try:
        sms = SMS.objects.get(id=id)
    except SMS.DoesNotExist:
        return False

    #create recipients list
    recipients_list = []
    for group_item in SMSRecipientGroupThrough.objects.filter(sms_id=id):
        for item in RecipientThrough.objects.filter(group_id = group_item.group_id):
            recipients_list.append([item.recipient.phone, group_item.group.description])

    for item in SMSRecipientThrough.objects.filter(sms_id=id): #sms.sms_recipient.all():
        recipients_list.append([item.recipient.phone, u''])

    #create sms items to recipients
    for item in uniquer(recipients_list):

        remote_id_temp=u''
        while True:
            remote_id_temp = u'%s' % os.urandom(16).encode('hex')
            sms_queue_count = SMSQueue.objects.filter(Q(remote_id = remote_id_temp)).count()
            if not sms_queue_count:
                break

        sms_queue = SMSQueue()
        sms_queue.phone = item[0]
        sms_queue.remote_id = remote_id_temp
        sms_queue.internal_sender = internal_sender
        sms_queue.internal_sms = sms
        if len(item[1]):
            sms_queue.text = u'%s\n******\n%s'%(item[1], sms.text)
        else:
            sms_queue.text = sms.text
        sms_queue.save()

    if sms.add_to_queue_count:
        sms.add_to_queue_count+=1
    else:
        sms.add_to_queue_count=1
    sms.save()