from django import http
from django.conf import settings
from django.utils import simplejson
from django.views.generic.list import MultipleObjectMixin
from django.views.generic.base import View
from django.core.paginator import InvalidPage
from django.core.urlresolvers import reverse


class BaseMixin(object):

    def get_context_data(self):
        return {}


class JSONResponseMixin(BaseMixin):

    def render_to_response(self, context):
        "Returns a JSON response containing 'context' as payload"
        return self.get_json_response(self.convert_context_to_json(context))

    def get_json_response(self, content, **httpresponse_kwargs):
        "Construct an `HttpResponse` object."
        return http.HttpResponse(content,
                                 content_type='application/json',
                                 **httpresponse_kwargs)

    def convert_context_to_json(self, context):
        "Convert the context dictionary into a JSON object"
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.

        return simplejson.dumps(context)


class ObjectListMixin(MultipleObjectMixin, BaseMixin, View):

    paginate_by = getattr(settings, 'PAGINATION__PER_PAGE', 20)

    paginate_url = None

    def paginate_queryset(self, queryset, page_size):
        """
        Paginate the queryset, if needed.
        """
        paginator = self.get_paginator(queryset, page_size, allow_empty_first_page=self.get_allow_empty())
        page = self.kwargs.get('page') or self.request.GET.get('page') or self.request.POST.get('page') or 1
        try:
            page_number = int(page)
        except ValueError:
            if page == 'last':
                page_number = paginator.num_pages
            else:
                raise http.Http404(_(u"Page is not 'last', nor can it be converted to an int."))
        try:
            page = paginator.page(page_number)
            return (paginator, page, page.object_list, page.has_other_pages())
        except InvalidPage:
            raise http.Http404(_(u'Invalid page (%(page_number)s)') % {
                                'page_number': page_number
            })

    def get_next_page_url(self, paginator, page):
        if self.paginate_url and page.has_next():
            paginate_url = reverse(self.paginate_url)
            return '%s?page=%s' % (paginate_url, page.next_page_number())

        return None

    def get_prev_page_url(self, paginator, page):
        if self.paginate_url and page.has_previous():
            paginate_url = reverse(self.paginate_url)
            return '%s?page=%s' % (paginate_url, page.previous_page_number())

        return None

    def get_object_list(self, queryset):
        items = []
        for item in queryset:
            items.append({
                "available_for": item.available_for,
                "lat": item.latitude, "long": item.longitude,
                "location": item.location_description,
                "url": item.get_absolute_url(),
                "skills": [{'name': t.name} for t in item.skills.all()],
                "user": {"name": item.name,
                         "username": item.user.username},
                })

        return items
