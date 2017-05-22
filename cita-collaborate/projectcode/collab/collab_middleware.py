from django.http import HttpResponseRedirect
from django.core import urlresolvers
from collab.profiles.models import UserProfile
from collab.profiles.views2 import create_profile

class CheckProfileExistence(object):
    """Every user should have a profile. This middleware won't allow the user to do anything
    until he/she creates a profile."""
    def process_request(self, request):
        if 'accounts' in request.path or 'profile' in request.path:
            return None
        if request.user.is_anonymous() or request.user.is_superuser:
            return None
        try:
            request.user.get_profile()
            return None
        except UserProfile.DoesNotExist:
#            return HttpResponseRedirect(urlresolvers.reverse('profiles_create_profile', kwargs={'success_url': urlresolvers.reverse('join_leave_projects', kwargs={'join_or_leave': 'join'})}))
            return create_profile(request, success_url=urlresolvers.reverse('join_leave_projects', kwargs={'join_or_leave': 'join'}))

class RemoveAnonymousMessage(object):
    """Removes the anonymous message key in the sessions, if one is present."""
    
    def process_request(self, request):
        # Inelegant way to do this, but it works. 
        if 'messagecounter' not in request.session:
            request.session['messagecounter']=0
        if 'message_anonymous' in request.session:
            request.session['messagecounter'] += 1
            if request.session['messagecounter'] > 1:
                del request.session['message_anonymous']
                request.session['messagecounter']=0
        return None
