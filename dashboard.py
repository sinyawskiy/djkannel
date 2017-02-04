#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from admin_tools.dashboard import modules, Dashboard, AppIndexDashboard
from admin_tools.utils import get_admin_site_name


class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard for ort.
    """
    title = u'Администрирование. ИС "SMS оповещение"'
    
    def init_with_context(self, context):

        site_name = get_admin_site_name(context)

        # append an app list module for "Applications"
        self.children.append(modules.AppList(
            title=_('Applications'),
            layout='inline',
            draggable=False,
            deletable=False,
            collapsible=False,
            exclude=('django.contrib.*',),# 'authority.*'),
        ))

        # append a link list module for "quick links"
        self.children.append(modules.LinkList(
            title=_('Quick links'),
            layout='inline',
            draggable=False,
            deletable=False,
            collapsible=False,
            children=[
                [_('Return to site'), '/'],
                [u'phpMyAdmin', '/phpmyadmin/'],
                [u'Статус KANNEL', '/kannelmonitor/'],
                [u'Тест KANNEL', '/kannelsendsms/']
              #  [_('Change password'),
              #   reverse('%s:password_change' % site_name)],
               # [_('Log out'), reverse('%s:logout' % site_name)],
            ]
        ))
        # append an app list module for "Administration"

        self.children+=[modules.ModelList(
            title = u'Администрирование',
            layout='inline',
            draggable=False,
            deletable=False,
            collapsible=False,
            models = (
                'django.contrib.auth.*',
                #'authority.*',
            )
        ),]


class CustomAppIndexDashboard(AppIndexDashboard):
    """
    Custom app index dashboard for ort.
    """

    # we disable title because its redundant with the model list module
    title = ''

    def __init__(self, *args, **kwargs):
        AppIndexDashboard.__init__(self, *args, **kwargs)
        # append a model list module and a recent actions module
        self.children += [
            modules.ModelList(_(self.app_title), self.models),

            modules.RecentActions(
                _('Recent Actions'),
                include_list=self.get_app_content_types(),
                limit=5
            )
        ]


    def init_with_context(self, context):
        """
        Use this method if you need to access the request context.
        """
        return super(CustomAppIndexDashboard, self).init_with_context(context)

