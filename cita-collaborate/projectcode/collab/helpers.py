from collab.project.models import Privilege, Role
from django.contrib.auth.models import User
from collab.project.models import CollabProject
from django.http import HttpResponseRedirect
from collab.forms import DeleteForm
from django.shortcuts import render_to_response
from django.template import RequestContext


def is_allowed(request,  project_id, model_name, perm_type):
    """
    Checks if a user has privileges to perform the action.
    
    Note: If AnonymousRole has access, then so will anyone.
    Note 2: Site admin (i.e. superuser) has all privileges.
    Note 3: Project admin has all privileges for the project.

    Note 4: Unless one is a superuser, one needs to be in the group to
        perform the action. It's quite possible that a user will still
        be in that role (although the interface doesn't show it) - but
        if he's not in the group, then he can't do anything.
    
    perm_type is either "Editable" or "Viewable". Anything else raises
    a ValueError exception.
    """
    
    model_name = model_name.lower()
    
    if perm_type not in [elem[0] for elem in Privilege.TYPE_CHOICES]:
        raise ValueError("Wrong value for perm_type!")
    
    privilege = Privilege.objects.get(project__id=project_id,  related_model__exact=model_name,  permission_type=perm_type)
    
    if request.user.is_superuser:
        return True
    
    list_of_roles = Role.objects.filter(privileges=privilege, project__id=project_id)
    
    AnonymousRole = Role.objects.get(project__id=project_id, name='AnonymousRole')
    if AnonymousRole in list_of_roles:
        return True
    
    if not request.user.is_active:
        return False
    
    allowed_users = User.objects.filter(roles__in=list_of_roles)
    
    project = CollabProject.objects.get(id=project_id)
    
    if not project.users.filter(id=request.user.id):
        return False
    
    if project.admin.filter(id=request.user.id):
        return True
    
    if request.user not in allowed_users:
        return False
    else:
        return True

def handle_privilege(request, message='', redirect_url=''):
    """
    If the user has permissions, carry on. Otherwise give a message and
    redirect. This function also handles the case in which the user is
    anonymous (i.e. not send a message).
    """
    
    if not request.user.is_authenticated():
        request.session['message_anonymous'] = message
    else:
        request.user.message_set.create(message=message)
    return HttpResponseRedirect(redirect_url)

def delete_anything(request, object, deleted_url, not_deleted_url, delete_template='delete.html', project=None):
    """
    A generic view to delete an object.
    """
    
    object_name = object.__class__._meta.verbose_name
    if project==None:
        project = object.project
    
    if request.method == 'POST':
        form = DeleteForm(request.POST)
        if "Yes" in request.POST:
            object.delete()
            message = "The %s was deleted." % object_name
            return handle_privilege(request, message, deleted_url)
        else:
            message = "The %s was not deleted." % object_name
            return handle_privilege(request, message, not_deleted_url)
    else:
        form = DeleteForm()
    return render_to_response(delete_template, {'form': form,  'description': 'this %s' % object_name, 'project': project}, context_instance=RequestContext(request))

def cluster_by(f, lst):
    transformed = [f(x) for x in lst]
    d = dict()
    for t, i in zip(transformed, lst):
        d.setdefault(t, []).append(i)
    return d.values()

