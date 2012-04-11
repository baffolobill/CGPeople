"""
This code is heavily based on samples found here -
http://www.b-list.org/weblog/2006/06/14/django-tips-template-context-processors

It is used to add some common variables to all the templates
"""
from django.conf import settings as site_settings
from django.contrib.sites.models import Site


def _get_site_url():
    protocol = getattr(site_settings, "PROTOCOL", "http")
    domain = Site.objects.get_current().domain
    port = getattr(site_settings, "PORT", "")
    if port:
        assert port.startswith(":"), "The PORT setting must have a preceeding ':'."

    return "%s://%s%s" % (protocol, domain, port)

def settings(request):

    ctx = {
        'request' : request,
        'site_url': _get_site_url(),
    }

    return ctx
