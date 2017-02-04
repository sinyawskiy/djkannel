#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This file was generated with the custommenu management command, it contains
the classes for the admin menu, you can customize this class as you want.

To activate your custom menu add the following to your settings.py::
    ADMIN_TOOLS_MENU = 'ort.menu.CustomMenu'
"""
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from admin_tools.menu import items, Menu
from admin_tools.menu.items import MenuItem


class HistoryMenuItem(MenuItem):
    title = _('History')

    def init_with_context(self, context):
        request = context['request']
        # we use sessions to store the visited pages stack
        history = request.session.get('history', [])
        for item in history:
            self.children.append(MenuItem(
                title=item['title'],
                url=item['url']
            ))
        # add the current page to the history
        new_title = u'Неизвестный заголовок'
        if 'title' in context:
            new_title = context['title']
        if request.path == u'/admin/password_change/':
            new_title = u'Изменение пароля'


        history.insert(0, {
            'title': new_title,
            'url': request.META['PATH_INFO']
        })
        if len(history) > 10:
            history = history[:10]
        request.session['history'] = history

class CustomMenu(Menu):
    """
    Custom Menu for ort admin site.
    """
    def __init__(self, **kwargs):
        Menu.__init__(self, **kwargs)
        self.children += [
            items.MenuItem(_('Dashboard'), reverse('admin:index')),
            items.Bookmarks(),
            items.AppList(
                _('Applications'),
                exclude=('django.contrib.*',)#'authority.*')
            ),
            items.AppList(
                _('Administration'),
                models=('django.contrib.*',)#'authority.*')
            ),
            HistoryMenuItem
        ]

    def init_with_context(self, context):
        """
        Use this method if you need to access the request context.
        """
        return super(CustomMenu, self).init_with_context(context)
