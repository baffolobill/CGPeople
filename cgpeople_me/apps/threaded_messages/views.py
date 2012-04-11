# -*- coding:utf-8 -*-
import datetime

from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_noop
from django.core.urlresolvers import reverse
from django.conf import settings
from django.template.loader import render_to_string

from threaded_messages.models import *
from threaded_messages.forms import ComposeForm, ReplyForm

from generic.views import JSONResponse

@login_required
def inbox(request, template_name='threaded_messages/inbox.html'):
    """
    Displays a list of received messages for the current user.
    Optional Arguments:
        ``template_name``: name of the template to use.
    """
    thread_list = []
    archive_list = []
    was = {'thread': [], 'archive': []}
    for item in Participant.objects.inbox_for(request.user):
        if item.thread.id in was['thread']: continue
        thread_list.append(item)
        was['thread'].append(item.thread.id)

    for item in Participant.objects.archive_for(request.user):
        if item.thread.id in was['archive']: continue
        archive_list.append(item)
        was['archive'].append(item.thread.id)

    return render_to_response(template_name, {
        'thread_list': thread_list,
        'archive_list': archive_list,
    }, context_instance=RequestContext(request))


def compose(request, recipient=None, form_class=ComposeForm):
    if len(request.POST.get('winnie_the_pooh', '')):
        return JSONResponse({"success": 1, 'message': _(u"Message successfully sent.")})

    try:
        recipient = User.objects.get(username=recipient)  #, id=request.POST.get('user_id', 0))
    except:
        return JSONResponse({'non_field_errors': {'0': 'Incorrect recipient: %s.'%recipient}})

    req_data = request.POST.copy()
    #req_data['recipient'] = recipient.id
    #if request.user.is_authenticated():
    #    req_data['sender'] = request.user.id
    sender = request.user if request.user.is_authenticated() else None

    form = form_class(data=req_data, sender=sender, recipient=recipient)
    if form.is_valid():
        instance = form.save()
        return JSONResponse({"success": 1, 'message': _(u"Message successfully sent.")})

    form_err = [(k,v[0]) for k, v in form.errors.items()]
    return JSONResponse({'field_errors': dict(form_err)})


@login_required
def delete(request, thread_id):
    """
    Marks a message as deleted by sender or recipient. The message is not
    really removed from the database, because two users must delete a message
    before it's save to remove it completely.
    A cron-job should prune the database and remove old messages which are
    deleted by both users.
    As a side effect, this makes it easy to implement a trash with undelete.
    """
    try:
        user = request.user
        thread = get_object_or_404(Thread, id=thread_id)
        user_part = get_object_or_404(Participant, user=user, thread=thread)
        user_part.deleted_at = datetime.datetime.now()
        user_part.save()
        return JSONResponse({'success': 1, 'message': "Message successfully deleted."})
    except:
        return JSONResponse({'error': 'Cannot remove message.'})

@login_required
def archive(request, thread_id):
    """
    Marks a message as archived by sender or recipient. The message is not
    really removed from the database, because two users must delete a message
    before it's save to remove it completely.
    A cron-job should prune the database and remove old messages which are
    deleted by both users.
    As a side effect, this makes it easy to implement a trash with undelete.
    """
    try:
        user = request.user
        thread = get_object_or_404(Thread, id=thread_id)
        user_part = get_object_or_404(Participant, user=user, thread=thread)
        user_part.archived_at = datetime.datetime.now()
        user_part.save()
        return JSONResponse({'success': 1, 'message': "Message successfully archived."})
    except:
        return JSONResponse({'error': 'Cannot archive message.'})


@login_required
def view(request, thread_id, form_class=ReplyForm,
        success_url=None, template_name='threaded_messages/view_ajax.html'):
    """
    Shows a single message.``message_id`` argument is required.
    The user is only allowed to see the message, if he is either
    the sender or the recipient. If the user is not allowed a 404
    is raised.
    If the user is the recipient and the message is unread
    ``read_at`` is set to the current datetime.
    """

    user = request.user
    thread = get_object_or_404(Thread, id=thread_id)

    """
    Reply stuff
    """
    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            thread, msg = form.save(sender=user, thread=thread)

            html = render_to_string('threaded_messages/message.html',
                RequestContext(request, {'msg': msg, 'thread': thread}))
            return JSONResponse({"success": 1, 'html': html,
                'message': _(u"Message successfully sent.")})

        form_err = [(k,v[0]) for k, v in form.errors.items()]
        return JSONResponse({'field_errors': dict(form_err)})

    else:
        form = form_class()

    now = datetime.datetime.now()
    participant = get_object_or_404(Participant, thread=thread, user=request.user)
    message_list = []
    for message in thread.all_msgs.all().order_by('sent_at'):
        unread = True
        if participant.read_at and message.sent_at <= participant.read_at:
            unread = False
        message_list.append((message,unread,))
    participant.read_at = now
    participant.save()

    html = render_to_string(template_name, {
        'thread': thread,
        'message_list': message_list,
        'form': form,
        'participant': participant,
        'others': participant.others(),
    }, context_instance=RequestContext(request))

    return JSONResponse({'success': 1, 'html': html, 'opponent': participant.others()[0].user_name})


def messages_count(request):
    if request.user.is_authenticated():
        return JSONResponse({'unread': inbox_count_for(request.user)})
    else:
        return JSONResponse({'unread': 0})
