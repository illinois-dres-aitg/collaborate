from django.contrib import admin
from models import CollabProject, Privilege, Role, ProjectMembership

class CollabProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', )
    filter_horizontal = ('users', )
    prepopulated_fields = {"slug": ("name",)}
admin.site.register(CollabProject, CollabProjectAdmin)

class PrivilegeAdmin(admin.ModelAdmin):
    list_display = ('project',  'related_model', 'permission_type' )
admin.site.register(Privilege, PrivilegeAdmin)

class RoleAdmin(admin.ModelAdmin):
    list_display = ('name',  'project', )
admin.site.register(Role, RoleAdmin)

class ProjectMembershipAdmin(admin.ModelAdmin):
    list_display = ('person', 'project', 'is_admin', )

admin.site.register(ProjectMembership, ProjectMembershipAdmin)
