from django.contrib import admin
from models import ActionItem

class ActionItemAdmin(admin.ModelAdmin):
    date_hierarchy = 'date_assigned'
    list_display = ('action',  'project')
    list_filter = ('project', )
admin.site.register(ActionItem, ActionItemAdmin)
