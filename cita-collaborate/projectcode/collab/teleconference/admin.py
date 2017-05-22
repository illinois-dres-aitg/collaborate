from django.contrib import admin
from models import TeleConference, Minutes

class TeleConferenceAdmin(admin.ModelAdmin):
    list_display = ('time',  'agenda',  'project')
    list_display_links = ('time', 'agenda')
    list_filter = ('project', )
    date_hierarchy = 'time'
admin.site.register(TeleConference, TeleConferenceAdmin)

class MinutesAdmin(admin.ModelAdmin):
    pass
admin.site.register(Minutes, MinutesAdmin)
