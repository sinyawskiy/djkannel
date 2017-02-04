#!/usr/bin/python
# -*- coding: utf-8 -*-
from django import forms
from sms_storage.models import SMS, SMSRecipientGroupThrough, SMSRecipientThrough, add_internal_sms_to_queue

class SMSForm(forms.ModelForm):
    add_to_queue = forms.BooleanField(label = u'Добавить в очередь', required=False, initial=True)

    def save(self, commit=True):
        instance = super(SMSForm, self).save(commit=False)
        def save_m2m_with_through():
            recipients = [t for t in self.cleaned_data['sms_recipient']]
            groups = [t for t in self.cleaned_data['sms_recipient_group']]
            if instance.id is None:
                instance.save()

            instance.sms_recipient.clear()
            instance.sms_recipient_group.clear()
            for recipient in recipients:
                if not SMSRecipientThrough.objects.filter(recipient = recipient, sms=instance).count():
                    m2 = SMSRecipientThrough.objects.create(recipient = recipient, sms=instance)
                    m2.save()

            for group in groups:
                if not SMSRecipientGroupThrough.objects.filter(group = group, sms=instance).count():
                    m2 = SMSRecipientGroupThrough.objects.create(group = group, sms=instance)
                    m2.save()

        if commit:
            instance.save()
        else:
            self.save_m2m = save_m2m_with_through
        return instance

    def clean(self):
        cleaned_data = super(SMSForm, self).clean()
        if not len(cleaned_data['sms_recipient']) and not len(cleaned_data['sms_recipient_group']):
            raise forms.ValidationError("Должно быть заполнено поле получатель или группа")
        return cleaned_data

    class Meta:
        model = SMS
  