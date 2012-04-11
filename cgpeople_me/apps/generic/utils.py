import urllib, urllib2

from django import http
from django.conf import settings
from django.utils import simplejson
from django.utils.encoding import smart_str
from django.contrib.sites.models import Site


class JSONResponse(http.HttpResponse):
    def __init__(self, data, **kwargs):
        defaults = {
          'content_type': 'application/json',
        }
        defaults.update(kwargs)
        super(JSONResponse, self).__init__(simplejson.dumps(data), defaults)


def get_lat_lng(location):

    # http://djangosnippets.org/snippets/293/
    # http://code.google.com/p/gmaps-samples/source/browse/trunk/geocoder/python/SimpleParser.py?r=2476
    # http://stackoverflow.com/questions/2846321/best-and-simple-way-to-handle-json-in-django
    # http://djangosnippets.org/snippets/2399/

    location = urllib.quote_plus(smart_str(location))
    if not len(location):
        return None

    url = 'http://maps.googleapis.com/maps/api/geocode/json?address=%s&sensor=false' % location
    response = urllib2.urlopen(url).read()
    result = simplejson.loads(response)
    if result['status'] == 'OK':
        coords = []
        for res in result['results']:
            coords.append({'lat': float(res['geometry']['location']['lat']),
                            'lng': float(res['geometry']['location']['lng']),
                            'type': res['types'][0],
                            'name': res['address_components'][0]['long_name'],
                            'country': res['address_components'][-1]['short_name']})
        return coords if len(coords) else None
    else:
        return None

def get_site_url():
    protocol = getattr(settings, "PROTOCOL", "http")
    domain = Site.objects.get_current().domain
    port = getattr(settings, "PORT", "")
    if port:
        assert port.startswith(":"), "The PORT setting must have a preceeding ':'."

    return "%s://%s%s" % (protocol, domain, port)
