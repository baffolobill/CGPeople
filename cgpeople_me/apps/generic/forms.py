import re

from django import forms
from django.forms.forms import BoundField
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from taggit.forms import TagField

from .models import Profile, PortfolioSite
from . import app_settings


class ProfileForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.service_fields = []
        for shortname, name, icon in app_settings.SERVICES:
            field = forms.CharField(
                max_length=255, required=False, label=name
            )
            self.fields['service_' + shortname] = field
            self.service_fields.append({
                'label': name,
                'shortname': shortname,
                'id': 'service_' + shortname,
                'icon': icon,
                'field': BoundField(self, field, 'service_' + shortname),
            })

        self.improvider_fields = []
        for shortname, name, icon in app_settings.IMPROVIDERS:
            field = forms.CharField(
                max_length=50, required=False, label=name
            )
            self.fields['im_' + shortname] = field
            self.improvider_fields.append({
                'label': name,
                'shortname': shortname,
                'id': 'im_' + shortname,
                'icon': icon,
                'field': BoundField(self, field, 'im_' + shortname),
            })

        if self.instance.is_paid:
            self.fields['page_url'].widget.attrs.pop('disabled')

    # Fields for creating a User object
    name = forms.CharField(max_length=50, required=True)
    email = forms.EmailField(required=False, widget=forms.TextInput(attrs={'type': 'email'}),
            help_text="We'll need your email address to send you notices about messages.")
    bio = forms.CharField(widget=forms.Textarea(attrs={'cols': 40, 'rows': 10}),
            required=False, help_text='Tell us a bit about you.')
    #location_description = forms.CharField(max_length=50, required=False,
    #        help_text="What you'd like others to see your location as.")
    page_url = forms.CharField(max_length=50, required=True,
            widget=forms.TextInput(attrs={'disabled': 'disabled', 'class': 'page_url__name'}))

    available_for = forms.ChoiceField(
        choices = (
            (0, 'Nothing'),
            (1, 'Freelance/Contract work'),
            (2, 'Full-time work'),
        ), required=True
    )

    skills = TagField(required=False, help_text="to pay the bills")

    hide_from_search = forms.BooleanField(required=False)

    def clean_email(self):
        email = self.cleaned_data['email']
        user = User.objects.filter(email=email).exclude(id=self.instance.user.pk)
        if len(user):
            raise forms.ValidationError('That e-mail is already in use')
        return email

    def clean_page_url(self):
        url = self.cleaned_data.get('page_url').lower()
        if re.search(r'[^-a-z0-9]', url):
            raise forms.ValidationError(_('Page url may contain only latin letters, numbers and minus sign.'))

        if url in app_settings.RESERVED_USERNAMES:
            raise forms.ValidationError(_('That page url is reserved.'))

        # check if user paid for that
        if not self.instance.is_paid and url != self.instance.username:
            raise forms.ValidationError(_('It is a paid service a change page url.'))

        if not len(Profile.objects.filter(page_url=url).exclude(user=self.instance.user)) \
            and not len(User.objects.filter(username=url).exclude(id=self.instance.user.id)):
            return url

        raise forms.ValidationError(_('That page url is already used.'))

    def save(self, **kw):
        super(ProfileForm, self).save(**kw)
        self.instance.user.email = self.cleaned_data['email']
        self.instance.user.save()

        for fieldname, (namespace, predicate) in \
            app_settings.MACHINETAGS_FROM_FIELDS.items():
            self.instance.machinetags.filter(
                namespace=namespace, predicate=predicate
            ).delete()
            if fieldname in self.cleaned_data and \
                   self.cleaned_data[fieldname].strip():
                value = self.cleaned_data[fieldname].strip()
                self.instance.add_machinetag(namespace, predicate, value)

    class Meta:
        model = Profile
        fields = ('name', 'email', 'bio', 'skills', 'available_for', 'page_url', 'hide_from_search')


class LocationForm(forms.ModelForm):
    latitude = forms.FloatField(min_value=-90, max_value=90)
    longitude = forms.FloatField(min_value=-180, max_value=180)

    class Meta:
        model = Profile
        fields = ('latitude', 'longitude', )


class PortfolioForm(forms.ModelForm):

    class Meta:
        model = PortfolioSite
        fields = ('id', 'title', 'url', 'description', )

