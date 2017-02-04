#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.query_utils import Q
from annoying.functions import id_generator

class Property(property):
    pass

phone_validator = RegexValidator('^[7]{1}[0-9]{10}$', message=u'Телефонный номер должен быть в формате (11 цифр, начинаться на 7, без "+"), смотреть http://en.wikipedia.org/wiki/List_of_country_calling_codes.')

class Recipient(models.Model):
    last_name = models.CharField(u'фамилия', max_length=255)
    first_name = models.CharField( u'имя', max_length=255)
    patronymic = models.CharField(u'отчество', max_length=255)
    male_sex = models.NullBooleanField(u'мужской пол', null=True)
    birth_date = models.DateField(u'дата рождения', blank=True, null=True)
    phone = models.CharField(u'телефонный номер', max_length=11, validators=[phone_validator,],)
    search_name = models.CharField(u'имя для поиска', max_length=255, help_text=u'заполняется автоматически', blank=True, unique=True)

    def save(self, *args, **kwargs):
        search_name = self.get_full_name()

        while True:
            cycle_name = u'%s %s' % (search_name, id_generator(4))
            recipient_count = Recipient.objects.filter(Q(search_name = cycle_name)).count()
            if not recipient_count:
                search_name = cycle_name
                break

        if not self.pk:
            while True:
                rand_number=id_generator(10)
                if not Recipient.objects.filter(Q(search_name = rand_number)).count():
                    break
            self.search_name = rand_number
            super(Recipient, self).save(*args, **kwargs)

        self.search_name = search_name

        super(Recipient, self).save(*args,**kwargs)


    class Meta:
        ordering = ['search_name']
        verbose_name = u'получатель'
        verbose_name_plural = u'получатели'

    def __unicode__(self):
        return u'%s(%s)' % (self.phone, self.get_full_name())

    def get_full_name(self):
        name = u'Аноним'
        if self.first_name:
            name = u'%s' % self.first_name
            if self.last_name:
                name = u'%s %s' % (self.last_name, name)
                if self.patronymic:
                    name = u'%s %s' % (name, self.patronymic)
        return name
    full_name=Property(get_full_name)
    full_name.short_description = u'Полное имя'


class GroupRecipient(models.Model):
    name = models.CharField(u'наименование группы', max_length=255)
    recipient = models.ManyToManyField(Recipient, verbose_name=u'получатель', through='RecipientThrough', related_name='recipient')
    description = models.CharField(u'описание', max_length=255, help_text=u'попадает в текст смс сообщения')
    password = models.CharField(u'пароль', max_length=255, help_text=u'для отправки на эту группу через POST (если пароль не указан на эту группу отправлять нельзя)', blank=True, null=True)
    max_message_len = models.IntegerField(u'максимальная длина сообщения', default=0, blank=True, help_text=u'если 0, то ограничения нет')
    
    class Meta:
        ordering = ['id']
        verbose_name = u'группа'
        verbose_name_plural = u'группы'

    def __unicode__(self):
        return u'%s(%s)' % (self.name, self.get_count_recipients())
    
    def save(self, *args, **kwargs):
        if not self.password:
            self.password = id_generator()
        super(GroupRecipient, self).save(*args,**kwargs)

    def get_count_recipients(self):
        return RecipientThrough.objects.filter(group=self.id).count()
    count_recipients= Property(get_count_recipients)
    count_recipients.short_description = u'Кол-во получателей'

class RecipientThrough(models.Model):
    recipient   = models.ForeignKey(Recipient, verbose_name=u'получатель', related_name='with_recipient')
    group = models.ForeignKey(GroupRecipient, verbose_name=u'группа', related_name='with_group_recipient')

    class Meta:
        ordering = ['id']
        verbose_name = u'связь группа получатель'
        verbose_name_plural = u'получатели по группам'
