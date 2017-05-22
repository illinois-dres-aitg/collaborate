from django.contrib import admin
from collab.registration.models import RegistrationProfile

class RegistrationProfileAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'activation_key_expired')
    search_fields = ('user__username', 'user__first_name')
admin.site.register(RegistrationProfile, RegistrationProfileAdmin)
