from django.contrib import admin
from . import models


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'profile_views')
    raw_id_fields = ('user',)


class PortfolioSiteAdmin(admin.ModelAdmin):
    pass

admin.site.register(models.Profile, ProfileAdmin)
admin.site.register(models.PortfolioSite, PortfolioSiteAdmin)
