import datetime
from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext_noop
from django.contrib.auth.models import User

from threaded_messages.models import *
#from django_messages.fields import CommaSeparatedUserField


class ComposeForm(forms.Form):
    """
    A form for creating a new message thread to one or more users.
    """
    #recipient = CommaSeparatedUserField(label=_(u"Recipient"))
    sender_name = forms.CharField(label=_(u"Name"))
    sender_email = forms.EmailField(label=_(u"Email"), required=False)
    #subject = forms.CharField(label=_(u"Subject"))
    message = forms.CharField(label=_(u"Body"),
        widget=forms.Textarea(attrs={'rows': '12', 'cols':'55'}))

    def __init__(self, sender, recipient, *args, **kwargs):
        #recipient_filter = kwargs.pop('recipient_filter', None)
        super(ComposeForm, self).__init__(*args, **kwargs)
        #if recipient_filter is not None:
        #    self.fields['recipient']._recipient_filter = recipient_filter
        self.sender = sender
        self.recipient = recipient

    def save(self):
        #recipients = self.cleaned_data['recipient']
        #subject = self.cleaned_data['subject']
        sender_name = self.cleaned_data['sender_name'] if not self.sender else self.sender.profile.name
        sender_email = self.cleaned_data['sender_email'] if not self.sender else self.sender.email
        message = self.cleaned_data['message']

        new_message = Message.objects.create(message=message,
            sender=self.sender,
            sender_name=sender_name,
            sender_email=sender_email)

        threads = [p.thread for p in Participant.objects.filter(
            user=self.sender, user_name=sender_name, user_email=sender_email,
            deleted_at__isnull=True, archived_at__isnull=True)]
        threads = [p.thread for p in Participant.objects.filter(
            user=self.recipient, deleted_at__isnull=True,
            archived_at__isnull=True, thread__in=threads)]

        if len(threads):
            thread = threads[0]
            new_message.parent_msg = thread.latest_msg
            new_message.save()
            thread.latest_msg = new_message
            thread.all_msgs.add(new_message)
            thread.save()
        else:
            thread = Thread.objects.create(latest_msg=new_message)
            thread.is_anonymous = True if not self.sender else False
            thread.all_msgs.add(new_message)
            thread.save()

            if self.recipient != self.sender:
                Participant.objects.create(thread=thread, user=self.recipient,
                    user_name=self.recipient.profile.name,
                    user_email=self.recipient.email)





            sender_part, created = Participant.objects.get_or_create(thread=thread,
                                    user=self.sender, user_name=sender_name,
                                    user_email=sender_email)
            sender_part.replied_at = sender_part.read_at = datetime.datetime.now()
            sender_part.save()

        signals.threaded_message_sent.send(sender=self, message=new_message)

        return thread

class ReplyForm(forms.Form):
    """
    A simpler form used for the replies.
    """
    message = forms.CharField(label=_(u"Reply"),
        widget=forms.Textarea(attrs={'rows': '4', 'cols':'55'}))

    def save(self, sender, thread):
        message = self.cleaned_data['message']

        new_message = Message.objects.create(message=message, sender=sender,
            sender_name=sender.profile.name, sender_email=sender.email)
        new_message.parent_msg = thread.latest_msg
        thread.latest_msg = new_message
        thread.all_msgs.add(new_message)
        thread.save()
        new_message.save()

        for participant in thread.participants.all():
            participant.deleted_at = None
            participant.archived_at = None
            participant.save()

        sender_part = Participant.objects.get(thread=thread, user=sender)
        sender_part.replied_at = sender_part.read_at = datetime.datetime.now()
        sender_part.save()

        signals.threaded_message_sent.send(sender=self, message=new_message)

        return thread, new_message
