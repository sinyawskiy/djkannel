#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from annoying.russian_admin import admin
from django.utils.translation import ugettext_lazy as _
from django.utils.text import capfirst
from django.db.models.base import ModelBase
from django.conf import settings
from pymorphy import get_morph
from pymorphy.templatetags.pymorphy_tags import inflect

morph = get_morph(settings.PYMORPHY_DICTS['ru']['dir'])

class I18nLabel():
    def __init__(self, function):
        self.target = function

    def rename(self, f, name = u''):
        def wrapper(*args, **kwargs):
            extra_context = kwargs.get('extra_context', {})
            extra_context['app_label'] = _(extra_context.get('app_label', args[0].model._meta.app_label.title()))
            if 'delete_view' != f.__name__:
                extra_context['title'] = self.get_title_by_name(f.__name__, args[1], name)
            else:
                if hasattr(self, 'current_name'):
                    extra_context['object_name'] = morph.inflect_ru(self.current_name, u'вн').lower()
                else:
                    #TODO: Изучить детальнее в дальнейшем возникает при удалении объекта связи
                    extra_context['object_name'] = u'not name'
            kwargs['extra_context'] = extra_context
            return f(*args, **kwargs)
        return wrapper

    def get_title_by_name(self, name, request={}, obj_name = u''):
        obj_name = unicode(obj_name)
        if 'add_view' == name:
            return _('Add %s') % inflect(obj_name, u'вн').lower()
        elif 'change_view' == name:
            return _('Change %s') % inflect(obj_name, u'вн').lower()
        elif 'changelist_view' == name:
            if 'pop' in request.GET:
                title = _('Select %s')
            else:
                title = _('Select %s to change')
            return title % inflect(obj_name, u'вн').lower()
        else:
            return ''

    def wrapper_register(self, model_or_iterable, admin_class=None, **option):
        ''' Изменяет имя приложения и breadcrumbs '''
        if isinstance(model_or_iterable, ModelBase):
            model_or_iterable = [model_or_iterable]
        for model in model_or_iterable:
            if admin_class is None:
                admin_class = type(model.__name__+'Admin', (admin.ModelAdmin,), {})
            current_name = model._meta.verbose_name.upper()
            admin_class.add_view = self.rename(admin_class.add_view, current_name)
            admin_class.change_view = self.rename(admin_class.change_view, current_name)
            admin_class.changelist_view = self.rename(admin_class.changelist_view, current_name)
            admin_class.delete_view = self.rename(admin_class.delete_view, current_name)
        return self.target(model_or_iterable, admin_class, **option)

    def wrapper_app_index(self, request, app_label, extra_context=None):
        ''' Изменяет breadcrumb для имени приложения в app_index.html
            Здесь же можно изменить h1 заголовок, добавив
            в extra_content {'title': self.app_label} '''
      #  requested_app_label = resolve(request.path).kwargs.get('app_label', '')
        if extra_context is None:
            extra_context = {}
        extra_context['title'] = _('%s administration') % _(capfirst(app_label))
        return self.target(request, app_label, extra_context)

    def register(self):
        return self.wrapper_register

    def index(self):
        return self.wrapper_app_index
