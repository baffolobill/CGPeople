from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.views.generic.simple import direct_to_template

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^iewarning/$', direct_to_template, {'template': 'iewarning.html'}, name='ie-warning'),
    url (r'', include('generic.urls')),
    url(r'^twitter/', include('twitter_users.urls')),
    url(r'^messages/', include('threaded_messages.urls')),
)

if settings.DEBUG:
    from django.views.static import serve
    from django.utils.http import http_date
    import time
    def static_view(request, path, document_root):
        response = serve(request, path, document_root)
        response['Cache-Control'] = 'no-cache'
        #response["Last-Modified"] = http_date(time.mktime(time.localtime()))
        return response

    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', static_view,
         {'document_root': settings.STATIC_ROOT}),
        (r'^media/(?P<path>.*)$', static_view,
         {'document_root': settings.MEDIA_ROOT}),
    )
