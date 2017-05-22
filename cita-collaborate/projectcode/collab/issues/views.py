from models import Issue, IssueSet, IssueImage
from django.views.generic import list_detail
from collab.project.models import CollabProject
from collab.helpers import is_allowed, handle_privilege, delete_anything
from django.http import HttpResponseRedirect
from forms import IssueSetForm, IssueForm, ImageForm
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

@login_required
def add_edit_issueset(request, *args, **kwargs):
    """Adds/Edits issue sets"""
    
    project_name = kwargs['project_name']
    project = get_object_or_404(CollabProject, slug=project_name)
    project_id = project.id

    if not is_allowed(request,  project_id,  IssueSet._meta.verbose_name,  'Editable'):
        return handle_privilege(request, "You do not have privileges to edit issue lists!", project.get_absolute_url())

    if 'issueset_id' in kwargs:
        issueset_id = kwargs['issueset_id']
        issueset = get_object_or_404(IssueSet, id=issueset_id)
        # Check if the issue set exists in that project!
        if issueset.project.id != project.id:
            return handle_privilege(request, "The issue list does not exist in that project!", project.get_absolute_url())
        edit = True
        instance=issueset
    else:
        edit = False
        instance=None
    
    if request.method == 'POST':
        form = IssueSetForm(request.POST, instance=instance)
        if form.is_valid():
            if not edit:
                issueset = IssueSet()
                message = "The issue list was added."
            else:
                message = "The issue list was modified."
            issueset = form.save(commit=False)
            issueset.project = project
            issueset.save()
            request.user.message_set.create(message=message)
            return HttpResponseRedirect(reverse('issuesets_overview', kwargs={'project_name': project.slug}))
    else:
        form = IssueSetForm(instance=instance)
    return render_to_response('issues/add_edit_issueset.html', {'form': form,  'edit': edit,  'project': project, 'issueset': instance}, context_instance=RequestContext(request))

def add_edit_issueset_breadcrumbs(args, kwargs):
    if 'issueset_id' in kwargs:
        issueset_id = kwargs['issueset_id']
        issueset = get_object_or_404(IssueSet, id=issueset_id)
        return 'Modify ' + issueset.name
    else:
        return 'Add a new issue list'

add_edit_issueset.breadcrumbs = add_edit_issueset_breadcrumbs

@login_required
def add_edit_issue(request, *args, **kwargs):
    """Adds/Edits issues"""
    
    project_name = kwargs['project_name']
    project = get_object_or_404(CollabProject, slug=project_name)
    project_id = project.id
    
    issueset_id = kwargs['issueset_id']
    issueset = get_object_or_404(IssueSet, id__exact=issueset_id)

    if not is_allowed(request,  project_id,  Issue._meta.verbose_name,  'Editable'):
        return handle_privilege(request, "You do not have privileges to edit issues!", issueset.get_absolute_url())

    if 'issue_id' in kwargs:
        issue_id = kwargs['issue_id']
        issue = get_object_or_404(Issue, id=issue_id)
        # Check if the issue exists in that project AND issue set!
        if issue.issueset.project.id != project.id or issue.issueset.id != issueset.id:
            return handle_privilege(request, "The issue does not match the project or issue list!", project.get_absolute_url())
        edit = True
        instance=issue
    else:
        edit = False
        instance=None

    if request.method == 'POST':
        form = IssueForm(request.POST, instance=instance, issueset=issueset)
        if form.is_valid():
            if not edit:
                issue = Issue()
                message = "The issue was added."
            else:
                message = "The issue was modified."
            issue = form.save(commit=False)
            
            if not edit:
                issue.reporter = request.user

#            issue.issueset = issueset
            issue.save()
            request.user.message_set.create(message=message)
            return HttpResponseRedirect(issue.get_absolute_url())
    else:
        form = IssueForm(initial={'issueset': issueset.pk},  instance=instance, issueset=issueset)
    return render_to_response('issues/add_edit_issue.html', {'form': form,  'edit': edit,  'project': project, 'issueset': issueset, 'issue': instance}, context_instance=RequestContext(request))

def add_edit_issue_breadcrumbs(args, kwargs):
    if 'issue_id' in kwargs:
        issue_id = kwargs['issue_id']
        issue = get_object_or_404(Issue, id=issue_id)
        return 'Modify ' + issue.title
    else:
        return 'Add a new issue'

add_edit_issue.breadcrumbs = add_edit_issue_breadcrumbs


def details_issueset(request, project_name,  issueset_id):
    """
    Takes in the issueset id and shows its details. If the user has
    permissions, it will allow him/her to delete as well.
    """

    project = get_object_or_404(CollabProject, slug=project_name)
    project_id = project.id
    issueset = get_object_or_404(IssueSet, id=issueset_id)

    # If the requested issueset item is of a different project, return to (a) project page.
    if issueset.project.id != project.id:
        return handle_privilege(request, "The issue list does not exist in that project!", project.get_absolute_url())

    if not is_allowed(request,  project_id,  IssueSet._meta.verbose_name,  'Viewable'):
        return handle_privilege(request, "You do not have privileges to view issue lists!", project.get_absolute_url())

    if is_allowed(request,  project_id,  IssueSet._meta.verbose_name,  'Editable'): 
        deletable = True
    else:
        deletable = False
        
    if is_allowed(request,  project_id,  Issue._meta.verbose_name,  'Editable'): 
        new_issue_perm = True
    else:
        new_issue_perm = False
    
    list_of_issues = issueset.issues.order_by('status', '-updated_date').all()
    list_of_issues = [{'number': issue.number, 'title': issue.title, 'last_modified': issue.updated_date, 'status': issue.status, 'url': issue.get_absolute_url()} for issue in list_of_issues]
    
    return render_to_response('issues/issuesetdetails.html', {'issueset': issueset, 'project': project, 'deletable': deletable, 'new_issue_perm': new_issue_perm, 'list_of_issues': list_of_issues}, context_instance=RequestContext(request))

#details_issueset.breadcrumbs = 'Issue List Details'
details_issueset.breadcrumbs = lambda args, kwargs: get_object_or_404(IssueSet, id=kwargs['issueset_id']).name

def details_issue(request, project_name, issueset_id, issue_id):
    """
    Takes in the issueset id and shows its details. If the user has
    permissions, it will allow him/her to delete as well.
    """

    project = get_object_or_404(CollabProject, slug=project_name)
    project_id = project.id
    issueset = get_object_or_404(IssueSet, id=issueset_id)
    issue = get_object_or_404(Issue, id=issue_id)

    # If the requested issueset is of a different project, return to (a)
    # project page.
    if issueset.project.id != project.id or issue.issueset.id != issueset.id:
        return handle_privilege(request, "The issue, issue list and project do not correspond!", project.get_absolute_url())

    if not is_allowed(request, project_id, Issue._meta.verbose_name, 'Viewable'):
        return handle_privilege(request, "You do not have privileges to view issues!", project.get_absolute_url())

    if is_allowed(request, project_id, Issue._meta.verbose_name, 'Editable'): 
        deletable = True
    else:
        deletable = False

    # Any logged in person who can view an issue should be able to
    # upload to it.
    if request.user.is_active and request.user.is_authenticated():
	logged_in = True
    else:
	logged_in = False

    # Create a flag to allow certain users to delete images.
    if request.user.is_superuser or request.user in project.admin.all():
	delete_image = True
    else:
	delete_image = False
    
    return render_to_response('issues/issuedetails.html', {'issue': issue, 'project': project, 'deletable': deletable, 'delete_image': delete_image, 'logged_in': logged_in}, context_instance=RequestContext(request))

details_issue.breadcrumbs = lambda args, kwargs: get_object_or_404(Issue, id=kwargs['issue_id']).title

@login_required
def delete_issueset(request, project_name, issueset_id):
    """
    Allows you to delete the action item. It verifys that the project
    and action item match.
    """
    
    project = get_object_or_404(CollabProject, slug=project_name)
    project_id = project.id
    issueset = get_object_or_404(IssueSet, id=issueset_id)

    if not is_allowed(request,  project_id,  IssueSet._meta.verbose_name,  'Editable'):
        return handle_privilege(request, "You do not have privileges to edit issue lists!", issueset.get_absolute_url())

    # If the requested action item is of a different project, return to (a) project page.
    if issueset.project.id != project.id:
        return handle_privilege(request, "The issue list does not exist in that project!", project.get_absolute_url())
    
    return delete_anything(request, issueset, reverse('issuesets_overview', kwargs={'project_name': project.slug}), reverse('issueset_details', kwargs={'project_name': project.slug, 'issueset_id': issueset.id}))

delete_issueset.breadcrumbs = lambda args, kwargs: "Delete " + get_object_or_404(IssueSet, id=kwargs['issueset_id']).name

@login_required
def delete_issue(request, project_name, issueset_id, issue_id):
    """
    Allows you to delete the action item. It verifys that the project
    and action item match.
    """

    project = get_object_or_404(CollabProject, slug=project_name)
    project_id = project.id
    issueset = get_object_or_404(IssueSet, id=issueset_id)
    issue = get_object_or_404(Issue, id=issue_id)

    # If the requested issueset is of a different project, return to (a) project page.
    if issueset.project.id != project.id or issue.issueset.id != issueset.id:
        return handle_privilege(request, "The issue, issue list and project do not correspond!", project.get_absolute_url())

    if not is_allowed(request, project_id, Issue._meta.verbose_name, 'Editable'):
        return handle_privilege(request, "You do not have privileges to edit issues!", issue.get_absolute_url())

    return delete_anything(request, issue, reverse('issueset_details', kwargs={'project_name': project.slug, 'issueset_id': issueset_id}), reverse('issue_details', kwargs={'project_name': project.slug, 'issueset_id': issueset_id, 'issue_id': issue_id}), project=issueset.project)


delete_issue.breadcrumbs = lambda args, kwargs: "Delete " + get_object_or_404(Issue, id=kwargs['issue_id']).title


def issuesets_overview(request, *args, **kwargs):
    """
    Shows all issue lists, with relevant links.
    """
    
    project_name=kwargs['project_name']
    project = get_object_or_404(CollabProject, slug=project_name)
    project_id=project.id
    
    if not is_allowed(request,  project_id,  IssueSet._meta.verbose_name,  'Viewable'):
        return handle_privilege(request, "You do not have privileges to view issues!", project.get_absolute_url())

    if is_allowed(request,  project_id,  IssueSet._meta.verbose_name,  'Editable'):
        editable = True
    else:
        editable = False

    issuesets_list = {
                          'queryset': IssueSet.objects.filter(project__id=project_id).filter(active=True).order_by('name'), 
                          'template_name': 'issues/overview.html', 
                          'template_object_name': 'active_issuesets', 
                          'extra_context': {'inactive_issuesets': IssueSet.objects.filter(project__id=project_id).filter(active=False).order_by('name'), 'project': project, 'editable': editable}, 
                        }
    
    return list_detail.object_list(request, **issuesets_list)

issuesets_overview.breadcrumbs = 'Issue Lists Overview'

def details_issueset_flat(request, project_name,  issueset_id):
    """
    Takes in the issueset id and shows all the issues - paginated and
    sorted by date.
    """

    project = get_object_or_404(CollabProject, slug=project_name)
    project_id = project.id
    issueset = get_object_or_404(IssueSet, id=issueset_id)

    # If the requested issueset item is of a different project, return to (a) project page.
    if issueset.project.id != project.id:
        return handle_privilege(request, "The issue list does not exist in that project!", project.get_absolute_url())

    if not is_allowed(request,  project_id,  IssueSet._meta.verbose_name,  'Viewable'):
        return handle_privilege(request, "You do not have privileges to view issue lists!", project.get_absolute_url())

    issue_dict = {
                  'paginate_by': 20, 
                  'queryset': issueset.issues.order_by('-updated_date').all(), 
                  'template_name': 'issues/issueset_latest.html', 
                  'extra_context': {'project': project, 'issueset': issueset}, 
                  'template_object_name': 'issues'
                }
    
    return list_detail.object_list(request, **issue_dict)
details_issueset_flat.breadcrumbs = 'Latest issues'

def issues_flat(request, project_name):
    """
    Shows all the issues of a given project - paginated and sorted by
    date.
    """

    project = get_object_or_404(CollabProject, slug=project_name)
    project_id = project.id
#    issueset = get_object_or_404(IssueSet, id=issueset_id)

#    # If the requested issueset item is of a different project, return to (a) project page.
#    if issueset.project.id != project.id:
#        return handle_privilege(request, "The issue list does not exist in that project!", project.get_absolute_url())

    if not is_allowed(request,  project_id,  IssueSet._meta.verbose_name,  'Viewable'):
        return handle_privilege(request, "You do not have privileges to view issues!", project.get_absolute_url())

    issue_dict = {
                  'paginate_by': 20, 
                  'queryset': Issue.objects.filter(issueset__project__id=project_id).order_by('-updated_date').all(), 
                  'template_name': 'issues/issues_latest.html', 
                  'extra_context': {'project': project,}, 
                  'template_object_name': 'issues'
                }
    
    return list_detail.object_list(request, **issue_dict)
issues_flat.breadcrumbs = 'Latest issues'

@login_required
def upload_image(request, project_name, issueset_id, issue_id):
    """
    View for uploading the image and attaching it to an issue.
    """

    project = get_object_or_404(CollabProject, slug=project_name)
    project_id = project.id
    issueset = get_object_or_404(IssueSet, id=issueset_id)
    issue = get_object_or_404(Issue, id=issue_id)

    
    if not is_allowed(request, project_id, Issue._meta.verbose_name, 'Editable'):
        return handle_privilege(request, "You do not have privileges to edit issues!", issueset.get_absolute_url())

    # Check if the issue exists in that project AND issue set!
    if issue.issueset.project.id != project.id or issue.issueset.id != issueset.id:
	return handle_privilege(request, "The issue does not match the group or issue list!", project.get_absolute_url())

    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
	    # In Django 1.02, I need the following hack. The reason is
	    # that to decide where to upload the file to, it need to
	    # know what issue it is attached to. When I execute
	    # form.save(commit=False), it fails (although not in the
	    # current SVN).
	    form.cleaned_data["issue"] = issue
            image = form.save(commit=False)
            image.issue = issue
            image.save()
	    message = "The image has been added to the issue."
            request.user.message_set.create(message=message)
            return HttpResponseRedirect(issue.get_absolute_url())
    else:
        form = ImageForm()
    return render_to_response('issues/add_image.html', {'form': form, 'issue': issue, 'project': project}, context_instance=RequestContext(request))
upload_image.breadcrumbs = 'Add image'

@login_required
def delete_issue(request, image_id):
    """
    Delete an attachmemt. Currently, you have to be a group admin to do
    so.
    """

    image = get_object_or_404(IssueImage, id=image_id)
    project = image.issue.issueset.project
    issue = image.issue

    if not (request.user in project.admin.all() or request.user.is_superuser):
        return handle_privilege(request, "You do not have privileges to delete images!", issue.get_absolute_url())

    return delete_anything(request, image,
			   reverse('issue_details', kwargs={'project_name': project.slug, 'issueset_id': issue.issueset.id, 'issue_id': issue.id}),
			   reverse('issue_details', kwargs={'project_name': project.slug, 'issueset_id': issue.issueset.id, 'issue_id': issue.id}),
			   project=project)
delete_issue.breadcrumbs = "Delete image"
