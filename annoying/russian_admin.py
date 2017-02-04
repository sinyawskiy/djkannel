# -*- coding: utf-8 -*-
"""
Для поддержки русского языка замените у себя в проекте
``from django.contrib import admin`` на ``from russian_admin import admin``.
"""

from __future__ import absolute_import
from django.contrib import admin
from django.contrib.admin import sites
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from annoying.breadcrumbs import I18nLabel

class ModelAdmin(admin.ModelAdmin):
    pass

class AdminSite(sites.AdminSite):

    app_index_template = 'admin/app_index.html'

    def register(self, model_or_iterable, admin_class=None, **options):
        if admin_class is None:
            # по умолчанию используем наш ModelAdmin
            admin_class = ModelAdmin

        return super(AdminSite, self).register(model_or_iterable, admin_class, **options)


admin.site = AdminSite()
admin.site.register = I18nLabel(admin.site.register).register()
admin.site.app_index = I18nLabel(admin.site.app_index).index()