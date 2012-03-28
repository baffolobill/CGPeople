from django import http
from django.db.models import Q
from django.conf import settings
from django.views.generic import TemplateView
from django.views.generic.base import TemplateResponseMixin, View
from django.utils import simplejson
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.contrib.gis.measure import D
from django.contrib.gis.geos import Point, fromstr
from django.contrib.auth import logout

from cities.models import City
from django_messages.models import Message

from machinetags.utils import tagdict
from machinetags.models import MachineTaggedItem
from . import app_settings, models, forms
from .mixins import *
from .utils import get_lat_lng, JSONResponse


class BaseView(JSONResponseMixin, TemplateResponseMixin, View):

    template_name = ''

    def render_to_response(self, context):
        # Look for a 'format=json' GET argument
        if self.request.is_ajax():
            return JSONResponseMixin.render_to_response(self, context)
        else:
            return TemplateResponseMixin.render_to_response(self, context)



    def get_context_data(self, **kwargs):
        """
        Get the context for this view.
        """
        queryset = kwargs.pop('object_list') if 'object_list' in kwargs else self.get_queryset()
        page_size = self.get_paginate_by(queryset)

        paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, page_size)
        context = {'meta': {'next': self.get_next_page_url(paginator, page),
                            'previous': self.get_prev_page_url(paginator, page),
                            'count': paginator.count, 'num_pages': paginator.num_pages,
                            'limit': page_size},
                    'objects': self.get_object_list(queryset)}

        return context


class ObjectListView(ObjectListMixin, JSONResponseMixin):

    paginate_url = 'api-profile'

    queryset = models.Profile.objects.all()

    paginate_by = 500

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()

        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Get the context for this view.
        """
        queryset = kwargs.pop('object_list') if 'object_list' in kwargs else self.get_queryset()
        page_size = self.get_paginate_by(queryset)

        paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, page_size)
        context = {'meta': {'next': self.get_next_page_url(paginator, page),
                            'previous': self.get_prev_page_url(paginator, page),
                            'count': paginator.count, 'num_pages': paginator.num_pages,
                            'limit': page_size},
                    'objects': self.get_object_list(queryset)}

        return context


class SearchView(ObjectListMixin, JSONResponseMixin):

    paginate_url = 'search'

    queryset = models.Profile.objects.all()

    paginate_by = 500

    def post(self, request, *args, **kwargs):
        qs = self.search()
        context = self.get_context_data(object_list=qs)

        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        """
        Get the context for this view.
        """
        queryset = kwargs.pop('object_list') if 'object_list' in kwargs else self.get_queryset()
        page_size = self.get_paginate_by(queryset)

        paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, page_size)
        context = {'meta': {'next': self.get_next_page_url(paginator, page),
                            'previous': self.get_prev_page_url(paginator, page),
                            'count': paginator.count, 'num_pages': paginator.num_pages,
                            'limit': page_size},
                    'objects': self.get_object_list(queryset)}

        return context


    def search(self):
        loc = unicode(self.request.POST.get('location', '')).strip()
        try:
            distance = int(self.request.POST.get('distance', 0))
        except:
            distance = 0
        skills = unicode(self.request.POST.get('skills', '')).strip()

        try:
            available_for = int(self.request.POST.get('available_for', 0))
        except:
            available_for = 0

        qs = self.queryset
        if len(skills):
            qs = qs.filter(skills__name__in=[s.strip() for s in skills.split(',')])

        # filter by available for field
        if available_for > 0:
            qs = qs.filter(available_for=available_for)

        # location might be city, region or country
        coords = get_lat_lng(loc)
        if coords:
            qry = None
            distance_query = []
            for crd in coords:
                if crd['type'] == 'locality':
                    fld = Q(country__code=crd['country'])&Q(city__name=crd['name'])
                elif crd['type'] == 'country':
                    fld = Q(country__code=crd['country'])
                else:
                    fld = Q(country__code=crd['country'])&Q(city__region__name__istartswith=crd['name'])
                    fld |= Q(country__code=crd['country'])&Q(city__region__region_parent__name__istartswith=crd['name'])

                if distance > 0:
                    distance_query.append(Point(crd['lng'], crd['lat']))

                    #fld &= Q(coords__distance_lte=(pnt, D(m=distance)))

                if not qry:
                    qry = fld
                else:
                    qry |= fld

            qs1 = qs.filter(qry)

            if len(distance_query):
                qs2 = qs.none()
                for pnt in distance_query:
                    qs2 |= qs.extra(
                        #where=['ST_DWithin(coords, ST_PointFromText(%s, 4326), %s)'],
                        #where=['ST_Distance(coords, ST_PointFromText(%s, 4326)) <= %s'],
                        where=["round(CAST(ST_Distance_Sphere(ST_Centroid(coords), ST_PointFromText(%s, 4326)) As numeric),2) <= %s"],
                        params=[pnt.wkt, D(mi=distance).m]
                    )

                qs = qs1 | qs2
            else:
                qs = qs1



        if not coords and not len(skills):
            qs = self.queryset.none()

        return qs




def geocode(request):
    location = request.POST.get('search', '')
    coord = get_lat_lng(location)
    if coord:
       return JSONResponse({'lat': coord[0]['lat'], 'lng': coord[0]['lng'], 'success': True})
    else:
        return JSONResponse({"success": False})

def skill_list(request):
    from taggit.models import Tag

    q = unicode(request.GET.get('q', '')).strip()
    if len(q) == 0:
        return http.HttpResponse('')

    was = []
    items = []
    for t in Tag.objects.distinct().filter(name__istartswith=q)[:10]:
        tname = unicode(t.name).lower().strip()
        if tname not in was:
            was.append(tname)
            items.append(tname)
    return http.HttpResponse('\n'.join(items))


class BrowseView(TemplateView):
    template_name = "browse.html"

    def get_context_data(self, **kwargs):
        kwargs = super(BrowseView, self).get_context_data(**kwargs)
        return kwargs


class ProfileView(TemplateView):
    template_name = "view_profile.html"

    def get_context_data(self, **kwargs):
        kwargs = super(ProfileView, self).get_context_data(**kwargs)

        profile = get_object_or_404(models.Profile, user__username=kwargs['params']['username'])
        profile.profile_views += 1
        profile.save()

        kwargs.update({"cloudmade_key": settings.CLOUDMADE_API_KEY})

        mtags = tagdict(profile.machinetags.all())

        # Set up convenient iterables for IM and services
        ims = []
        for key, value in mtags.get('im', {}).items():
            shortname, name, icon = app_settings.IMPROVIDERS_DICT.get(key, ('', '', ''))
            if not shortname:
                continue  # Bad machinetag
            ims.append({
                'shortname': shortname,
                'name': name,
                'value': value,
            })
        ims.sort(lambda x, y: cmp(x['shortname'], y['shortname']))

        services = {}
        for key, value in mtags.get('services', {}).items():
            shortname, name, icon = app_settings.SERVICES_DICT.get(key, ('', '', ''))
            if not shortname:
                continue  # Bad machinetag
            #services.append({
            #    'shortname': shortname,
            #    'name': name,
            #    'value': value,
            #})
            services[shortname] = {'name': name, 'value': value}
        #services.sort(lambda x, y: cmp(x['shortname'], y['shortname']))

        kwargs.update({
            'is_owner': self.request.user.username == kwargs['params']['username'],
            'profile': profile,
            'mtags': mtags,
            'ims': ims,
            'services': services,
            'user': self.request.user,
            'closest_users': None, #profile.get_nearest(20),
        })


        return kwargs


class EditProfileView(TemplateView):
    template_name = "edit_profile.html"

    def get_context_data(self, **kwargs):
        kwargs = super(EditProfileView, self).get_context_data(**kwargs)
        kwargs.update({"cloudmade_key": settings.CLOUDMADE_API_KEY})

        profile = get_object_or_404(models.Profile, user__username=self.request.user.username)
        mtags = tagdict(profile.machinetags.all())

        profile_form = forms.ProfileForm(initial={'name': profile.name, 'email': profile.user.email,
            'bio': profile.bio, 'skills': ', '.join([s.name for s in profile.skills.all()]),
            'available_for': profile.available_for,
            'service_facebook': mtags['services']['facebook'],
            'service_linkedin': mtags['services']['linkedin'],
            'service_freelancercom': mtags['services']['freelancercom'],
            'service_flickr': mtags['services']['flickr']})
        kwargs.update({'profile_form': profile_form})
        kwargs.update({'profile': profile})

        return kwargs


class SaveProfileView(JSONResponseMixin, View):

    def post(self, request, *args, **kwargs):
        profile = get_object_or_404(models.Profile, user=self.request.user)
        form = forms.ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return self.render_to_response({"success": "Your profile has been updated."})

        form_err = [(k,v[0]) for k, v in form.errors.items()]
        return self.render_to_response({'field_errors': dict(form_err)})


class SavePositionView(JSONResponseMixin, View):

    def post(self, request, *args, **kwargs):
        profile = get_object_or_404(models.Profile, user__username=self.request.user.username)
        form = forms.LocationForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            pnt = Point(profile.longitude, profile.latitude)
            profile.coords = pnt
            closest_cities = City.objects.distance(profile.coords).order_by('distance')
            if len(closest_cities):
                profile.country = closest_cities[0].country
                profile.city = closest_cities[0]
                profile.location_description = '%s, %s' % (profile.city.name, profile.country.name)
            profile.save()

            return self.render_to_response({"success": "Your location has been successfully updated."})

        return self.render_to_response({"errors": "Cannot update your position."})


class DeleteProfileView(TemplateView):

    template_name = 'delete_profile.html'


class ReallyDeleteProfileView(View):

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated():
            return redirect('index')

        profile = get_object_or_404(models.Profile, user=self.request.user)
        profile.portfoliosite_set.all().delete()
        #profile.skills.all().delete()
        profile.user.twitterinfo.delete()
        Message.objects.filter(recipient=profile.user).delete()
        Message.objects.filter(sender=profile.user).update(sender=None)
        profile.user.delete()
        profile.delete()
        logout(request)

        # redirect to home page
        return redirect('index')


class AddSiteView(JSONResponseMixin, View):

    def post(self, request, *args, **kwargs):
        profile = get_object_or_404(models.Profile, user=self.request.user)
        form = forms.PortfolioForm(request.POST)
        if form.is_valid():
            pflio = form.save(commit=False)
            pflio.profile = profile
            pflio.save()
            html = render_to_string('generic/_portfolio_site.html', {'site': pflio})
            return self.render_to_response({"message": "Portfolio site has been added.",
                    "success": True, "response": html})

        form_err = [(k,v[0]) for k, v in form.errors.items()]
        return self.render_to_response({'field_errors': dict(form_err)})


class EditSiteView(JSONResponseMixin, View):

    def post(self, request, *args, **kwargs):
        profile = get_object_or_404(models.Profile, user=self.request.user)
        portfolio_site = get_object_or_404(models.PortfolioSite, id=self.request.POST.get('id', -1))
        form = forms.PortfolioForm(request.POST, instance=portfolio_site)
        if form.is_valid():
            pflio = form.save(commit=False)
            pflio.profile = profile
            pflio.save()
            html = render_to_string('generic/_portfolio_site.html', {'site': pflio})
            return self.render_to_response({"message": "Portfolio site updated.",
                    "success": True, "response": html})

        form_err = [(k,v[0]) for k, v in form.errors.items()]
        return self.render_to_response({'field_errors': dict(form_err)})


class DeleteSiteView(JSONResponseMixin, View):

    def get(self, request, *args, **kwargs):
        profile = get_object_or_404(models.Profile, user=self.request.user)
        item = get_object_or_404(models.PortfolioSite, id=kwargs['object_id'], profile=profile)
        item.delete()

        return self.render_to_response({'success': True})


class HideTweetView(JSONResponseMixin, View):

    def get(self, request, *args, **kwargs):
        profile = get_object_or_404(models.Profile, user=self.request.user)
        profile.show_tweet = False
        profile.save()
        return self.render_to_response({'success': True})


class IndexView(TemplateView):

    template_name = "index.html"

    def get_context_data(self, **kwargs):
        kwargs = super(IndexView, self).get_context_data(**kwargs)
        kwargs.update({"cloudmade_key": settings.CLOUDMADE_API_KEY})
        return kwargs


class PrivacyView(TemplateView):

    template_name = "privacy.html"
