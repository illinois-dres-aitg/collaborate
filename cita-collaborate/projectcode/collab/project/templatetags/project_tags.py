from django import template
from collab.project.models import CollabProject
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from collab.helpers import is_allowed

register = template.Library()

def is_project_admin(userid, project_slug):
    """A filter that takes in a project_slug. If the user corresponding
    to the userid is an admin of the project,  return True. Else, 
    return False."""
    
    try:
        project = CollabProject.objects.get(slug=project_slug)
    except ObjectDoesNotExist:
        return ''
    if project.admin.filter(id=userid):
        return True
    else:
        return False

register.filter('is_project_admin', is_project_admin)

#def get_roles(userid, project_slug):
#    """A filter that takes in a project_slug. If the user corresponding
#    to the userid is an admin of the project,  return True. Else, 
#    return False."""
#    
#    try:
#        project = CollabProject.objects.get(slug=project_slug)
#    except ObjectDoesNotExist:
#        return ''
#    if project.admin.filter(id=userid):
#        return True
#    else:
#        return False
#
#register.filter('is_project_admin', is_project_admin)
