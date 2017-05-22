from collab.project.models import CollabProject
from models import ActionItem
from forms import ActionItemForm
from collab.helpers import is_allowed, handle_privilege, delete_anything
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.generic import list_detail
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

@login_required
def add_edit_action(request,  *args,  **kwargs):
    """Takes in the project id and (if editing) the action_id and allows you to add/edit an action item."""

    project_name=kwargs['project_name']
    project = get_object_or_404(CollabProject, slug=project_name)
    project_id=project.id
    
    if not is_allowed(request, project_id, ActionItem._meta.verbose_name,  'Editable'):
        return handle_privilege(request, "You do not have privileges to edit action items!", project.get_absolute_url())
    
    if 'action_id' in kwargs:
        action_id = kwargs['action_id']
        action_item = get_object_or_404(ActionItem, id=action_id)
        # Check if the action item exists in that project!
        if action_item.project.id != project.id:
            return handle_privilege(request, "The action item does not exist in that project!", project.get_absolute_url())
        edit = True
        instance=action_item
    else:
        edit = False
        instance=None
    
    if request.method == 'POST':
        form = ActionItemForm(project.id,  request.POST,  instance=instance)
        if form.is_valid():
            if not edit:
                action = ActionItem()
                message = "The action item was added."
            else:
                message = "The action item was modified."
            action = form.save(commit=False)
            action.project = project
            action.save()
            form.save_m2m()
            request.user.message_set.create(message=message)
	    return HttpResponseRedirect(reverse('action_details', kwargs={'project_name': project.slug, 'action_id': action.id}))
    else:
        form = ActionItemForm(project.id,  instance=instance)

    return render_to_response('action/add_edit_action.html', {'form': form, 'edit': edit, 'project': project, 'action': instance}, context_instance=RequestContext(request))

def add_edit_action_breadcrumbs(args, kwargs):
    if 'action_id' in kwargs:
        return 'Modify action item'
    else:
        return 'Add an action item'

add_edit_action.breadcrumbs = add_edit_action_breadcrumbs

def details(request, project_name,  action_id):
    """Takes in the action item id and shows its details. If the user has permissions, it will allow him/her to delete as well."""

    project = get_object_or_404(CollabProject, slug=project_name)
    project_id = project.id
    action_item = get_object_or_404(ActionItem, id=action_id)

    if not is_allowed(request,  project_id, ActionItem._meta.verbose_name,  'Viewable'):
        return handle_privilege(request, "You do not have privileges to view action items!", project.get_absolute_url())

    # If the requested action item is of a different project, return to (a) project page.
    if action_item.project.id != project.id:
        return handle_privilege(request, "The action item does not exist in that project!", project.get_absolute_url())

    if is_allowed(request,  project_id,  ActionItem._meta.verbose_name,  'Editable'): 
        deletable = True
    else:
        deletable = False
    
    return render_to_response('action/actiondetails.html', {'action': action_item, 'project': project, 'deletable': deletable}, context_instance=RequestContext(request))

details.breadcrumbs = 'Details'

@login_required
def delete_action(request, project_name, action_id):
    """Allows you to delete the action item. It verifys that the project and action item match."""
    
    project = get_object_or_404(CollabProject, slug=project_name)
    project_id = project.id
    action_item = get_object_or_404(ActionItem, id=action_id)

    if not is_allowed(request,  project_id,  ActionItem._meta.verbose_name,  'Editable'):
        return handle_privilege(request, "You do not have privileges to edit action items!", action_item.get_absolute_url())

    # If the requested action item is of a different project, return to (a) project page.
    if action_item.project.id != project.id:
        return handle_privilege(request, "The action item does not exist in that project!", project.get_absolute_url())

    return delete_anything(request, action_item,
                           reverse('action_overview', kwargs={'project_name': project.slug}), 
                           reverse('action_details', kwargs={'project_name': project.slug, 'action_id': action_id})
                        )

delete_action.breadcrumbs = 'Delete'

#    delete_action_info = {
#                          'model': ActionItem, 
#                          'object_id': action_item.id, 
#                          'post_delete_redirect': reverse('action_overview', kwargs={'project_name': project.slug}), 
#                          'template_name': 'action/delete_action.html', 
#                          'extra_context': {'project': project}
#                        }
#    
#    return create_update.delete_object(request,  **delete_action_info)

def action_overview(request, *args, **kwargs):
    """Shows a summary of action items, with relevant links"""
    
    project_name=kwargs['project_name']
    project = get_object_or_404(CollabProject, slug=project_name)
    project_id=project.id
    
    if not is_allowed(request,  project_id,  ActionItem._meta.verbose_name,  'Viewable'):
        return handle_privilege(request, "You do not have privileges to view action items!", project.get_absolute_url())

    if is_allowed(request,  project_id,  ActionItem._meta.verbose_name,  'Editable'):
        editable = True
    else:
        editable = False

    action_items_list = {
                          'queryset': ActionItem.objects.filter(project__id=project_id).filter(status='Open').order_by('deadline'), 
                          'template_name': 'action/overview.html', 
                          'template_object_name': 'open_action_items', 
                          'extra_context': {'closed_action_items': ActionItem.objects.filter(project__id=project_id).filter(status='Closed').order_by('-deadline'), 'canceled_action_items': ActionItem.objects.filter(project__id=project_id).filter(status='Canceled').order_by('-deadline'), 'project': project, 'editable': editable}, 
                        }
    
    return list_detail.object_list(request, **action_items_list)
action_overview.breadcrumbs = 'Action Items'
