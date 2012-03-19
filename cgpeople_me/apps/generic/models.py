from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.html import escape
from django.contrib.gis.measure import Distance
from django.contrib.gis.geos import Point

from cities.models import Country, City
from cities.util import geo_distance
from machinetags.models import MachineTaggedItem, add_machinetag
from taggit.managers import TaggableManager


class Profile(models.Model):
    user = models.OneToOneField(User)
    name = models.CharField(max_length=255)
    bio = models.TextField(blank=True)

    # Location stuff - all location fields are required
    country = models.ForeignKey(Country, blank=True, null=True)
    city = models.ForeignKey(City, blank=True, null=True)
    latitude = models.FloatField(default=0)
    longitude = models.FloatField(default=0)
    coords = models.PointField(blank=True, null=True)
    location_description = models.CharField(max_length=50, blank=True, null=True)

    # Stats
    profile_views = models.IntegerField(default=0)

    # Machine tags
    machinetags = generic.GenericRelation(MachineTaggedItem)
    add_machinetag = add_machinetag
    skills = TaggableManager()

    created_on = models.DateTimeField(auto_now_add=True, editable=False)
    modified_on = models.DateTimeField(auto_now=True, editable=False)

    available_for = models.IntegerField(
        choices = (
            (0, 'Nothing'),
            (1, 'Freelance/Contract work'),
            (2, 'Full-time work'),
        ), default=0
    )
    show_tweet = models.BooleanField(default=True)

    objects = models.GeoManager()

    def get_nearest(self, num=5):
        "Returns the nearest X people, but only within the same continent"
        # TODO: Add caching

        people = list(self.country.profile_set.select_related().exclude(pk=self.id))
        if len(people) <= num:
            # Not enough in country; use people from the same continent instead
            people = list(Profile.objects.filter(
                country__continent=self.country.continent,
            ).exclude(pk=self.id).select_related())

        # Sort and annotate people by distance
        for person in people:
            person.distance_in_miles = Distance(km=geo_distance(
                Point(self.longitude, self.latitude),
                Point(person.longitude, person.latitude)
            )).mi

        # Return the nearest X
        people.sort(key=lambda x: x.distance_in_miles)
        return people[:num]

    def __unicode__(self):
        return unicode(self.name)

    def get_absolute_url(self):
        return reverse('profile', args=[self.user.username])

    def save(self, force_insert=False, force_update=False, **kwargs): # TODO: Put in transaction
        # Update country and region counters
        super(Profile, self).save(force_insert=False, force_update=False, **kwargs)
        #self.country.num_people = self.country.profile_set.count()
        #self.country.save()
        #if self.region:
        #    self.region.num_people = self.region.profile_set.count()
        #    self.region.save()

    class Meta:
        verbose_name_plural = 'CG People'


class PortfolioSite(models.Model):
    id = models.AutoField(primary_key=True, max_length=11)
    title = models.CharField(max_length=100)
    url = models.URLField(max_length=255)
    description = models.TextField(blank=True)
    profile = models.ForeignKey(Profile)

    def __unicode__(self):
        return '%s <%s>' % (self.title, self.url)

