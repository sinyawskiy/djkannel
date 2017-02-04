#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models
from annoying.functions import id_generator

alphabetic_validator = RegexValidator('^[A-Za-z]+$', message=u'Только латинские символы')
alphabetic_and_numeric_validator = RegexValidator('^[A-Za-z0123456789]+$', message=u'Только латинские символы и цифры')

class SMSGatewayUser(models.Model):
    name = models.CharField(u'имя', max_length=25, validators=[alphabetic_validator,], unique=True)
    password = models.CharField(u'пароль', max_length=25, validators=[alphabetic_and_numeric_validator,], blank=True, default=id_generator())
    create_date = models.DateTimeField(u'дата и время создания', auto_now_add=True)
    creator = models.ForeignKey(User, verbose_name=u'создатель', related_name='creator_with_auth_user', blank=True)
    description = models.TextField(u'описание')
    max_message_len = models.IntegerField(u'максимальная длина сообщения', default=0, blank=True, help_text=u'если 0, то ограничения нет')

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = u'пользователь шлюза'
        verbose_name_plural = u'пользователи шлюза'
    