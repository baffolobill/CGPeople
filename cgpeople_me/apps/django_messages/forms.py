import datetime
from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext_noop
from django.contrib.auth.models import User
import uuid

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

from django_messages.models import Message
from django_messages.utils import format_quote


class MessageForm(forms.ModelForm):
    """
    base message form
    """

    class Meta:
        model = Message
        fields = ('sender', 'sender_name', 'sender_email', 'recipient', 'message')

    def save(self, commit=True):
        instance = super(MessageForm, self).save(commit=False)

        if commit:
            instance.save()

        return instance


class ComposeForm(MessageForm):
    """
    A simple default form for private messages.
    """
    pass


class ReplyForm(MessageForm):
    """
    reply to form
    """
    class Meta:
        model = Message
        fields = ()



