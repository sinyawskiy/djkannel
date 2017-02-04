#!/usr/bin/python
# -*- coding: utf-8 -*-
from django import forms
from recipients.models import GroupRecipient, RecipientThrough

class GroupRecipientForm(forms.ModelForm):

    def save(self, commit=True):
        instance = super(GroupRecipientForm, self).save(commit=False)

        def save_m2m_with_through():
            recipients = [t for t in self.cleaned_data['recipient']]
            if instance.id is None:
                instance.save()

            instance.recipient.clear()
            for recipient in recipients:
                if not RecipientThrough.objects.filter(recipient = recipient, group=instance).count():
                    m1 = RecipientThrough.objects.create(recipient = recipient, group=instance)
                    m1.save()

        if commit:
            instance.save()
            #save_m2m_with_through()
        else:
            self.save_m2m = save_m2m_with_through
        return instance

    class Meta:
        model = GroupRecipient