#!/usr/bin/python
# -*- coding: utf-8 -*-
import random
import string
from django.shortcuts import _get_queryset
from django.db.models import AutoField

def get_object_or_None(klass, *args, **kwargs):
    """
    Uses get() to return an object or None if the object does not exist.

    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the get() query.

    Note: Like with get(), an MultipleObjectsReturned will be raised if more than one
    object is found.
    """
    queryset = _get_queryset(klass)
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        return None

def copy_model_instance(obj):
    """
    Create a copy of a model instance.
    M2M relationships are currently not handled, i.e. they are not copied. (Fortunately, you don't have any in this case)
    See also Django #4027. From http://blog.elsdoerfer.name/2008/09/09/making-a-copy-of-a-model-instance/
    """
    initial = dict([(f.name, getattr(obj, f.name)) for f in obj._meta.fields if not isinstance(f, AutoField) and not f in obj._meta.parents.values()])
    return obj.__class__(**initial)

def id_generator(size=10, chars=string.ascii_uppercase + string.digits):
     return ''.join(random.choice(chars) for x in range(size))
    