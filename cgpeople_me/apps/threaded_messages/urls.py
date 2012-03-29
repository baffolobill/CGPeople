from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to

from threaded_messages.views import *

urlpatterns = patterns('',
    #url(r'^$', redirect_to, {'url': 'inbox/'}),
    url(r'^$', inbox, name='messages_inbox'),
    #url(r'^outbox/$', outbox, name='messages_outbox'),
    url(r'^archive/(?P<thread_id>[\d]+)/$', archive, name='messages_archive'),
    #url(r'^compose/$', compose, name='messages_compose'),
    url(r'^compose/(?P<recipient>[\-_\w]+)/$', compose, name='messages_compose_to'),
    url(r'^view/(?P<thread_id>[\d]+)/$', view, name='messages_detail'),
    url(r'^delete/(?P<thread_id>[\d]+)/$', delete, name='messages_delete'),
    #url(r'^undelete/(?P<thread_id>[\d]+)/$', undelete, name='messages_undelete'),
    #url(r'^trash/$', trash, name='messages_trash'),
    url(r'^count/$', messages_count, name="messages_count"),
)
