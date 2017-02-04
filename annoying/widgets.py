#!/usr/bin/python
# -*- coding: utf-8 -*-
# http://code.google.com/p/django-autocomplete/

from django import forms
from django.conf import settings
from django.db.models.query_utils import Q
from django.utils.safestring import mark_safe
from django.contrib import admin
from django.db import models
from django.http import HttpResponse, HttpResponseNotFound
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.contrib.admin.options import InlineModelAdmin
from django.utils.translation import ugettext as _
from django.utils.safestring import SafeUnicode
from django.utils.datastructures import MultiValueDict, MergeDict
from functools import update_wrapper

#from django.utils.decorators import method_decorator
#from django.views.decorators.csrf import csrf_protect
#from django.db import models, transaction, router
#csrf_protect_m = method_decorator( csrf_protect )

media_css={ 'all': ( '%sautocomplete_widget/jquery.autocomplete.css'%settings.MEDIA_URL, ) }
media_js=( '%sautocomplete_widget/jquery.autocomplete.js'%settings.MEDIA_URL, )


class ForeignKeySearchInput( forms.HiddenInput ):
    """
    A Widget for displaying ForeignKeys in an autocomplete search input
    instead in a <select> box.
    """
    class Media:
        css=media_css
        js=media_js

    input_type='hidden'		# чтобы не отрисовывать текстовое поле
    is_hidden=False			# Чтобы отрисовывать заголовок в Inline

    def label_for_value( self, value ):
        rel_name=self.search_fields[0].split( '__' )[0]

        key=self.rel.get_related_field().name
        obj=self.rel.to._default_manager.get( **{key: value} )

        return getattr( obj, rel_name )

    def __init__( self, rel, search_fields, attrs = None ):
        self.rel=rel
        self.search_fields=search_fields
        super( ForeignKeySearchInput, self ).__init__( attrs )

    def render( self, name, value, attrs = None ):
        if attrs is None:
            attrs={}
        rendered=super( ForeignKeySearchInput, self ).render( name, value, attrs )
        if value:
            label=self.label_for_value( value )
        else:
            label=u''

        return SafeUnicode( rendered+u'''
            <input type="text" id="lookup_%(name)s" value="%(label)s" size="40" search_fields="%(search_fields)s" app_label="%(app_label)s" model_name="%(model_name)s" autocomplete_mode="ForeignKey" class="to_autocomplete"/>
            <a class="deletelink" title="удалить связь" onclick="autocomplete_delete(this)">&nbsp;</a>
        '''%{
            'search_fields': ','.join( self.search_fields ),
            'MEDIA_URL': settings.MEDIA_URL,
            'model_name': self.rel.to._meta.module_name,
            'app_label': self.rel.to._meta.app_label,
            'label': label,
            'name': name,
            'value': value,
        }
        )

class ManyToManySearchInput( forms.MultipleHiddenInput ):
    """
    A Widget for displaying ForeignKeys in an autocomplete search input
    instead in a <select> box.
    """
    class Media:
        css=media_css
        js=media_js

    input_type='hidden'		# чтобы не отрисовывать текстовое поле
    is_hidden=False			# Чтобы отрисовывать заголовок в Inline

    def __init__( self, rel, search_fields, attrs = None ):
        self.rel=rel
        self.search_fields=search_fields
        super( ManyToManySearchInput, self ).__init__( attrs )
        self.help_text=u'Для поиска укажите хотя бы два символа'

    def value_from_datadict( self, data, files, name ):
        if isinstance( data, ( MultiValueDict, MergeDict ) ):
            res=data.getlist( name )
        else:
            res=data.get( name, None )

        return res

    def render( self, name, value, attrs = None ):
        if attrs is None:
            attrs={}

        if value is None:
            value=[]

        label = ''
        selected = ''
        rel_name = self.search_fields[0].split( '__' )[0]

        for id in value:
            obj=self.rel.to.objects.get( pk = id )
            item_label = getattr( obj, rel_name )
            if (name=='recipient' or name=='sms_recipient') and len(item_label):
                item_label=u'%s'%item_label[:-5]

            selected=selected+mark_safe( u"""
                <div class="to_delete deletelink" ><input type="hidden" name="%(name)s" value="%(value)s"/>%(label)s</div>"""
                )%{
                    'label': item_label,
                    'name': name,
                    'value': obj.id,
        }


        return mark_safe( u'''
            <input type="text" id="lookup_%(name)s" value="" size="40" search_fields="%(search_fields)s" app_label="%(app_label)s" model_name="%(model_name)s" autocomplete_mode="ManyToMany"  class="to_autocomplete"/>%(label)s
            <div style="float:left; padding-left:105px; width:300px;">
            <font  style="color:#999999;font-size:10px !important;">%(help_text)s</font>
            <div id="box_%(name)s" style="padding-left:20px;cursor:pointer;">
                %(selected)s
            </div></div>
        ''' )%{
            'search_fields': ','.join( self.search_fields ),
            'model_name': self.rel.to._meta.module_name,
            'app_label': self.rel.to._meta.app_label,
            'label': label,
            'name': name,
            'value': value,
            'selected':selected,
            'help_text':self.help_text
        }

class AutocompleteModelAdmin( admin.ModelAdmin ):
    def __call__( self, request, url ):
        if url is None:
            pass
        elif url=='search':
            return self.search( request )
        return super( AutocompleteModelAdmin, self ).__call__( request, url )


    def get_urls( self ):
        from django.conf.urls import patterns, url

        def wrap( view ):
            def wrapper( *args, **kwargs ):
                return self.admin_site.admin_view( view )( *args, **kwargs )
            return update_wrapper( wrapper, view )

        info=self.model._meta.app_label, self.model._meta.module_name

        urlpatterns=patterns( '',
            url( r'^$', 			wrap( self.changelist_view ), name = '%s_%s_changelist'%info ),
            url( r'^add/$', 		wrap( self.add_view ), 		name = '%s_%s_add'%info ),
            url( r'^(.+)/history/$', wrap( self.history_view ), name = '%s_%s_history'%info ),
            url( r'^(.+)/delete/$', wrap( self.delete_view ), 	name = '%s_%s_delete'%info ),
            url( r'^search/$', 		wrap( self.search_view ), 	name = '%s_%s_search'%info ),
            url( r'^(.+)/$', 		wrap( self.change_view ), 	name = '%s_%s_change'%info ),
        )
        return urlpatterns

    def search_view( self, request ):

        #	Searches in the fields of the given related model and returns the
        #	result as a simple string to be used by the jQuery Autocomplete plugin

        query=request.GET.get( 'q', None )
        app_label=request.GET.get( 'app_label', None )
        model_name=request.GET.get( 'model_name', None )
        search_fields=request.GET.get( 'search_fields', None )

        query_arr = query.split(' ')

        if search_fields and app_label and model_name and query:
            def construct_search( field_name ):
                # use different lookup methods depending on the notation
                if field_name.startswith( '^' ):
                    return "%s__istartswith"%field_name[1:], field_name[1:]
                elif field_name.startswith( '=' ):
                    return "%s__iexact"%field_name[1:], field_name[1:]
                elif field_name.startswith( '@' ):
                    return "%s__search"%field_name[1:], field_name[1:]
                else:
                    return "%s__icontains"%field_name, field_name

            model=models.get_model( app_label, model_name )
            main_criteria = Q()
            fields=[]

            for field_name in search_fields.split( ',' ):
                name, name1=construct_search( field_name )
                fields.append( name1 )
                for query_item in query.split(' '):
                    main_criteria.add(Q(**{str( name ):query_item}), Q.AND)

            qs=model.objects.filter(main_criteria)

            data=''
            for f in qs[0:10]:
                res=[]
                for field in fields:

                    parts=field.split( '__' )
                    if len( parts )>1:
                        s='%s'%getattr( getattr( f, parts[0] ), parts[1] )
                    else:
                        s='%s'%getattr( f, parts[0] )
                    if s and s not in res:
                        if field_name == u'search_name':
                            res.append(u'%s'%s[:-5])
                        else:
                            res.append(s)
                data+=u'%s|%s\n'%( ', '.join( res ), f.pk )
            return HttpResponse( data )

#			rel_name=field_name.split( '__' )[0]
#
#			data=''.join( [u'%s|%s\n'%( getattr( f, rel_name ), f.pk ) for f in qs] )
#			return HttpResponse( data )
        return HttpResponseNotFound()

    def formfield_for_dbfield( self, db_field, **kwargs ):
        # For ForeignKey use a special Autocomplete widget.
        if isinstance( db_field, models.ForeignKey ) and db_field.name in self.related_search_fields:
            kwargs['widget']=ForeignKeySearchInput( db_field.rel,
                                    self.related_search_fields[db_field.name] )

            # extra HTML to the end of the rendered output.
            if 'request' in kwargs.keys():
                kwargs.pop( 'request' )

            formfield=db_field.formfield( **kwargs )
            # Don't wrap raw_id fields. Their add function is in the popup window.
            if not db_field.name in self.raw_id_fields:
                # formfield can be None if it came from a OneToOneField with
                # parent_link=True
                if formfield is not None:
                    formfield.widget=AutocompleteWidgetWrapper( formfield.widget, db_field.rel, self.admin_site )
            return formfield

        # For ManyToManyField use a special Autocomplete widget.
        if isinstance( db_field, models.ManyToManyField )and db_field.name in self.related_search_fields:
            kwargs['widget']=ManyToManySearchInput( db_field.rel,
                                    self.related_search_fields[db_field.name] )
            db_field.help_text=''

            # extra HTML to the end of the rendered output.
            if 'request' in kwargs.keys():
                kwargs.pop( 'request' )

            formfield=db_field.formfield( **kwargs )
            # Don't wrap raw_id fields. Their add function is in the popup window.
            if not db_field.name in self.raw_id_fields:
                # formfield can be None if it came from a OneToOneField with
                # parent_link=True
                if formfield is not None:
                    formfield.widget=AutocompleteWidgetWrapper( formfield.widget, db_field.rel, self.admin_site )
            return formfield

        return super( AutocompleteModelAdmin, self ).formfield_for_dbfield( db_field, **kwargs )


class AutocompleteWidgetWrapper( RelatedFieldWidgetWrapper ):
    def render( self, name, value, *args, **kwargs ):
        rel_to=self.rel.to
        related_url='../../../%s/%s/'%( rel_to._meta.app_label, rel_to._meta.object_name.lower() )
        self.widget.choices=self.choices
        output=[self.widget.render( name, value, *args, **kwargs )]
        if rel_to in self.admin_site._registry: # If the related object has an admin interface:
            # TODO: "id_" is hard-coded here. This should instead use the correct
            # API to determine the ID dynamically.
            output.append( u'<a href="%sadd/" class="add-another" id="add_id_%s" onclick="return showAutocompletePopup(this);"> '%\
                ( related_url, name ) )
            output.append( u'<img src="%simg/icon_addlink.gif" width="10" height="10" alt="%s"/></a>'%( settings.AUTOCOMPLETE_ADMIN_MEDIA_PREFIX, _( 'Add Another' ) ) )
        return mark_safe( u''.join( output ) )


class AutocompleteInlineModelAdmin( InlineModelAdmin ):

    def formfield_for_dbfield( self, db_field, **kwargs ):
        # For ForeignKey use a special Autocomplete widget.
        if isinstance( db_field, models.ForeignKey ) and db_field.name in self.related_search_fields:
            kwargs['widget']=ForeignKeySearchInput( db_field.rel,
                                    self.related_search_fields[db_field.name] )

            # extra HTML to the end of the rendered output.
            if 'request' in kwargs.keys():
                kwargs.pop( 'request' )

            formfield=db_field.formfield( **kwargs )
            # Don't wrap raw_id fields. Their add function is in the popup window.
            if not db_field.name in self.raw_id_fields:
                # formfield can be None if it came from a OneToOneField with

                if formfield is not None:
                    formfield.widget=AutocompleteWidgetWrapper( formfield.widget, db_field.rel, self.admin_site )
            return formfield

        # For ManyToManyField use a special Autocomplete widget.
        if isinstance( db_field, models.ManyToManyField )and db_field.name in self.related_search_fields:
            kwargs['widget']=ManyToManySearchInput( db_field.rel,
                                    self.related_search_fields[db_field.name] )
            db_field.help_text=''

            # extra HTML to the end of the rendered output.
            if 'request' in kwargs.keys():
                kwargs.pop( 'request' )

            formfield=db_field.formfield( **kwargs )
            # Don't wrap raw_id fields. Their add function is in the popup window.
            if not db_field.name in self.raw_id_fields:
                # formfield can be None if it came from a OneToOneField with
                # parent_link=True
                if formfield is not None:
                    formfield.widget=AutocompleteWidgetWrapper( formfield.widget, db_field.rel, self.admin_site )
            return formfield
        return super( AutocompleteInlineModelAdmin, self ).formfield_for_dbfield( db_field, **kwargs )


class AutocompleteStackedInline( AutocompleteInlineModelAdmin ):
    template='admin/edit_inline/stacked.html'

class AutocompleteTabularInline( AutocompleteInlineModelAdmin ):
    template='admin/edit_inline/tabular.html'




class WildModelSearchInput( forms.HiddenInput ):
    """
    A Widget for displaying ForeignKeys in an autocomplete search input
    instead in a <select> box.
    """
    class Media:
        css=media_css
        js=media_js

    input_type='hidden'
    is_hidden=False

    def label_for_value( self, value ):
        model=models.get_model( self.app_label, self.model_name )
        try:
            return model.objects.get( pk = value )
        except:
            return None

    def __init__( self, app_label, model_name, search_fields, attrs = None ):
        self.search_fields=search_fields
        self.app_label=app_label
        self.model_name=model_name
        super( WildModelSearchInput, self ).__init__( attrs )

    def render( self, name, value, attrs = None ):
        if attrs is None:
            attrs={}
        rendered=super( WildModelSearchInput, self ).render( name, value, attrs )
        if value:
            label=self.label_for_value( value )
        else:
            label=u''
        return rendered+mark_safe( u'''
            <input type="text" id="lookup_%(name)s" value="%(label)s" size="40" search_fields="%(search_fields)s" app_label="%(app_label)s" model_name="%(model_name)s" autocomplete_mode="ForeignKey"  class="to_autocomplete"/>
        '''%{
            'search_fields': ','.join( self.search_fields ),
            'MEDIA_URL': settings.MEDIA_URL,
            'model_name': self.model_name,
            'app_label': self.app_label,
            'label': label,
            'name': name,
            'value': value,
        } )
