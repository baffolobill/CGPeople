import datetime
from django.db import models
from django.conf import settings
from django.db.models import signals
from django.db.models.query import QuerySet
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from generic.models import Profile


class MessageManager(models.Manager):

    def inbox_for(self, user):
        """
        Returns all messages that were received by the given user and are not
        marked as deleted.
        """
        return self.filter(
            user=user,
            deleted_at__isnull=True,
            archived_at__isnull=True,
        )

    def archive_for(self, user):
        """
        Returns all messages that were archived by the given user and are not
        marked as deleted.
        """
        return self.filter(
            user=user,
            deleted_at__isnull=True,
            archived_at__isnull=False,
        )

    def trash_for(self, user):
        """
        Returns all messages that were either received or sent by the given
        user and are marked as deleted.
        """
        return self.filter(
            user=user,
            deleted_at__isnull=False,
        )

class Message(models.Model):
    """
    A private message from user to user
    """
    message = models.TextField(_("body"))
    sender = models.ForeignKey(User, related_name='sent_messages', blank=True, null=True, verbose_name=_("sender"))
    sender_name = models.CharField(max_length=50, verbose_name=_("Sender"), blank=True, null=True)
    sender_email = models.EmailField(blank=True, null=True)
    parent_msg = models.ForeignKey('self', related_name='next_messages', blank=True, null=True, verbose_name=_("parent message"))
    sent_at = models.DateTimeField(_("sent at"), auto_now_add=True)

    def __unicode__(self):
        return "%s - %s" % (str(self.sender), self.sent_at)

    def save(self, **kwargs):
        if not self.id:
            self.sent_at = datetime.datetime.now()
        super(Message, self).save(**kwargs)

    class Meta:
        ordering = ['-sent_at']
        verbose_name = _("Message")
        verbose_name_plural = _("Messages")

class Thread(models.Model):
    """
    A linear conversation between two or more Users
    """
    #subject = models.CharField(_("Subject"), max_length=120)
    latest_msg = models.ForeignKey(Message, related_name='thread_latest', verbose_name=_("Latest message"))
    all_msgs = models.ManyToManyField(Message, related_name='thread', verbose_name=_("Messages"))
    is_anonymous = models.BooleanField(default=False)

    def __unicode__(self):
        return "thread %s" % str(self.latest_msg) #self.subject

    def get_absolute_url(self):
        return ('messages_detail', [self.id])
    get_absolute_url = models.permalink(get_absolute_url)

    class Meta:
        ordering = ['latest_msg']
        verbose_name = _("Thread")
        verbose_name_plural = _("Threads")

class Participant(models.Model):
    """
    Thread manager for each participant
    """
    thread = models.ForeignKey(Thread, related_name='participants', verbose_name=_("message thread"))
    user = models.ForeignKey(User, related_name='threads', verbose_name=_("participant users"), blank=True, null=True)
    user_name = models.CharField(max_length=255, verbose_name=_("Sender"), blank=True, null=True)
    user_email = models.EmailField(blank=True, null=True)
    read_at = models.DateTimeField(_("read at"), null=True, blank=True)
    replied_at = models.DateTimeField(_("replied at"), null=True, blank=True)
    deleted_at = models.DateTimeField(_("deleted at"), null=True, blank=True)
    archived_at = models.DateTimeField(_("archived at"), null=True, blank=True)

    sender_profile = models.ForeignKey(Profile, blank=True, null=True)

    objects = MessageManager()

    def new(self):
        """returns whether the recipient has read the message or not"""
        if self.read_at is not None and self.read_at > self.thread.latest_msg.sent_at:
            return False
        return True

    def replied(self):
        """returns whether the recipient has read the message or not"""
        if self.replied_at is not None:
            return False
        return True

    def others(self):
        """returns the other participants of the thread"""
        return self.thread.participants.exclude(user=self.user)

    def __unicode__(self):
        return "%s"  % str(self.user)

    class Meta:
        ordering = ['thread']
        verbose_name = _("participant")
        verbose_name_plural = _("participants")


def inbox_count_for(user):
    """
    returns the number of unread messages for the given user but does not
    mark them seen
    """
    return sum([p.thread.all_msgs.filter(sent_at__gt=p.read_at).exclude(sender=user).count() \
            for p in Participant.objects.filter(user=user, archived_at__isnull=True, \
            deleted_at__isnull=True) if p.new()])


#import signals
#from utils import message_email_notification
#signals.threaded_message_sent.connect(message_email_notification)
