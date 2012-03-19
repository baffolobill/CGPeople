from django.conf.urls.defaults import patterns, url

from generic.views import *

urlpatterns = patterns('',
    url(r"^$", IndexView.as_view(), name="index"), # keep this last
    url(r"^privacy/$", PrivacyView.as_view(), name="privacy"),
    #url(r"^api/v1/profile/$", api__profile, name="api-profile"),
    url(r'^search/$', SearchView.as_view(), name="search"),
    url(r'^browse/$', BrowseView.as_view(), name="browse"),
    url(r"^api/v1/profile/$", ObjectListView.as_view(), name="api-profile"),

    url(r'^p/(?P<username>[-a-z0-9_]+)/$', ProfileView.as_view(), name="profile"),

    url(r'^profile/$', EditProfileView.as_view(), name="profile-edit"),
    url(r'^profile/save_position/$', SavePositionView.as_view(), name="profile-save-position"),
    url(r'^profile/save_profile/$', SaveProfileView.as_view(), name="profile-save-profile"),
    url(r'^profile/delete/$', DeleteProfileView.as_view(), name="profile-delete"),
    url(r'^profile/delete/really/$', ReallyDeleteProfileView.as_view(), name="profile-delete-really"),
    url(r'^profile/hide_tweet/$', HideTweetView.as_view(), name="profile-hide-tweet"),
    url(r'^profile/skills/$', skill_list, name="profile-skill-list"),

    url(r'^profile/site/add/$', AddSiteView.as_view(), name="profile-site-add"),
    url(r'^profile/site/edit/$', EditSiteView.as_view(), name="profile-site-edit"),
    url(r'^profile/site/delete/(?P<object_id>\d+)/$', DeleteSiteView.as_view(), name="profile-site-delete"),

    #url(r'^messages/$', MessagesView.as_view(), name="messages"),
    #url(r'^messages/count/$', messages_count, name="messages-count"),
    url(r'^geocode/$', geocode, name="geocode"),
)

