from django.contrib import admin
from models import SiteInfo

class SiteInfoAdmin(admin.ModelAdmin):
    pass
admin.site.register(SiteInfo, SiteInfoAdmin)
