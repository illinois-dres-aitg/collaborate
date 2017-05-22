from django.contrib import admin
from models import Issue, IssueSet, IssueImage

class IssueAdmin(admin.ModelAdmin):
    date_hierarchy = 'reported_date'
admin.site.register(Issue, IssueAdmin)

class IssueSetAdmin(admin.ModelAdmin):
    list_display = ('name', 'project')
    list_filter = ('project', )
admin.site.register(IssueSet, IssueSetAdmin)

class IssueImageAdmin(admin.ModelAdmin):
    list_display = ('desc', 'issue')
    list_filter = ('issue',)
admin.site.register(IssueImage, IssueImageAdmin)
