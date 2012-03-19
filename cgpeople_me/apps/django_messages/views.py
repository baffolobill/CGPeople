# -*- coding:utf-8 -*-
import datetime

from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_noop
from django.core.urlresolvers import reverse
from django.conf import settings

from django.db import transaction

from django.views.generic.list_detail import object_list, object_detail

from generic.views import JSONResponse

from django_messages.models import Message
from django_messages.forms import ComposeForm
from django_messages.utils import format_quote
from django_messages.models import inbox_count_for


@login_required
def message_list(request, queryset, paginate_by=500,
    extra_context=None, template_name=None):
    return object_list(request, queryset=queryset, paginate_by=paginate_by,
            extra_context=extra_context, template_name=template_name,
            template_object_name='message')


@login_required
def inbox(request, template_name='django_messages/inbox.html', **kw):
    """
    Displays a list of received messages for the current user.
    """
    kw['template_name'] = template_name
    kw['extra_context'] = {'profile': request.user.profile}
    queryset = Message.inbox.for_user(request.user)
    return message_list(request, queryset, **kw)


@transaction.commit_on_success
def compose(request, recipient, form_class=ComposeForm):
    if request.method == "POST":
        if len(request.POST.get('winnie_the_pooh', '')):
            return JSONResponse({"success": 1, 'message': _(u"Message successfully sent.")})

        try:
            recipient = User.objects.get(username=recipient, id=request.POST.get('user_id', 0))
        except:
            return JSONResponse({'non_field_errors': {'0': 'Incorrect recipient.'}})

        req_data = request.POST.copy()
        req_data['recipient'] = recipient.id
        if request.user.is_authenticated():
            req_data['sender'] = request.user.id

        form = form_class(data=req_data)
        if form.is_valid():
            instance = form.save()
            return JSONResponse({"success": 1, 'message': _(u"Message successfully sent.")})

        form_err = [(k,v[0]) for k, v in form.errors.items()]
        return JSONResponse({'field_errors': dict(form_err)})


@login_required
@transaction.commit_on_success
def delete(request, message_id):
    try:
        message = Message.objects.get(pk=message_id, recipient=request.user)
        message.move_to_trash()
        message.save()
        return JSONResponse({'success': 1, 'message': "Message successfully deleted."})
    except:
        return JSONResponse({'error': 'Cannot remove message.'})


@login_required
def messages_count(request):
    return JSONResponse({'unread': inbox_count_for(request.user)})
