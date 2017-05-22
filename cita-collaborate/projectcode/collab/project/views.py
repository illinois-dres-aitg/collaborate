from django.shortcuts import render_to_response, get_object_or_404
from models import CollabProject,  Role, Privilege, ProjectMembership
from forms import RoleForm, RoleBulkForm, MembersBulkForm, ProjectInfoForm, MembersActiveForm, BulkSubscriptionForm, CreateProjectForm, ProjectInfoAdminsForm, DocumentationForm, AnnouncementForm
from django.template import RequestContext, loader, Context
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import datetime
import time
from collab.helpers import is_allowed, handle_privilege, delete_anything
from collab.forms import DeleteForm
import collab.profiles.models
import collab.profiles.views2
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.core.mail import send_mail
from collab.settings import CONTACT_FROM_EMAIL
from django.views.generic import list_detail, create_update
from collab.siteinfo.models import SiteInfo
from collab.teleconference.models import TeleConference
from collab.action.models import ActionItem
from collab.issues.models import IssueSet

if collab.settings.DEBUG:
    import logging

def project_info(request,  project_name):
    """Takes in the project name and shows relevant project information.
    This serves as the main project page."""

    project = get_object_or_404(CollabProject, slug=project_name)
    project_id = project.id
    
#    import logging
#    logging.debug(dir(project))
#    logging.debug(project.__str__())
    
#    if not is_allowed(request, project.id, CollabProject._meta.verbose_name, 'Viewable'):
#        return handle_privilege(request, "You do not have privileges to view that project!", '/projects')

    privileges = {}
    if is_allowed(request, project.id, ActionItem._meta.verbose_name, 'Editable'):
        privileges['ActionEdit'] = True
    if is_allowed(request, project.id, ActionItem._meta.verbose_name, 'Viewable'):
        privileges['ActionView'] = True
    if is_allowed(request, project.id, TeleConference._meta.verbose_name, 'Editable'):
        privileges['TeleEdit'] = True
    if is_allowed(request, project.id, TeleConference._meta.verbose_name, 'Viewable'):
        privileges['TeleView'] = True
    if is_allowed(request, project.id, IssueSet._meta.verbose_name, 'Viewable'):
        privileges['IssueSetView'] = True
    if is_allowed(request, project.id, IssueSet._meta.verbose_name, 'Editable'):
        privileges['IssueSetEdit'] = True

    # I pass the conferences variable in the context separately as there is no way to do queries in templates.
    return render_to_response('project/projectpage.html',  {'project': project,  'privileges': privileges, 'conferences': project.teleconference.order_by('time').filter(time__gte=datetime.date.today())[0:5], 'actions': project.action_items.filter(status='Open').all(), 'issuesets': project.issuesets.filter(active=True).all()}, context_instance=RequestContext(request))

project_info.breadcrumbs = lambda args, kwargs: get_object_or_404(CollabProject, slug=args[0]).name

@login_required
def add_edit_role(request,  *args,  **kwargs):
    """Takes in the project id and allows you to add a new role."""

    project_name = kwargs['project_name']
    project = get_object_or_404(CollabProject, slug=project_name)
    id = project.id
    
    # If the user is not the project admin, just return him to the project page. 
    if not project.admin.filter(id=request.user.id) and not request.user.is_superuser:
        request.user.message_set.create(message="You do not have privileges to edit roles!")
        return HttpResponseRedirect(project.get_absolute_url())
    
    if 'role_id' in kwargs:
        role_id = kwargs['role_id']
        role = get_object_or_404(Role, id=role_id)
        # Check if the role exists in that project!
        if role.project.id != project.id:
            request.user.message_set.create(message="The role does not exist in that project!")
            return HttpResponseRedirect(project.get_absolute_url())
        edit, instance, initial = True, role, None
    else:
        edit, instance, initial = False, None, {}
    
    if request.method == 'POST':
        form = RoleForm(project.id,  request.POST, instance=instance, clean=(not edit), initial=initial)
        if form.is_valid():
            if not edit:
                new_role = Role()
                message = "The role was added."
            else:
                message = "The role was modified."
            new_role = form.save(commit=False)
            new_role.project = project
            new_role.save()
            # Need this as I have a many to many field and did commit=False.
            form.save_m2m()
            
            # It's possible that a user gave some Editable privileges without the corresponding Viewable. The 
            # following code automatically adds those Viewable privileges.
            for privilege in form.cleaned_data["privileges"]:
                if privilege.permission_type == 'Editable':
                    new_privilege = get_object_or_404(Privilege, project=project, related_model=privilege.related_model, permission_type='Viewable')
                    new_role.privileges.add(new_privilege)
            new_role.save()
            
            if form.cleaned_data["make_default"]==True:
                if project.default_role != new_role:
                    project.default_role = new_role
                    project.save()
            
            request.user.message_set.create(message=message)
            return HttpResponseRedirect(reverse('roles_overview', kwargs={'project_name': project.slug}))
    else:
        form = RoleForm(project.id, instance=instance, initial=initial)
    return render_to_response('project/addrole.html', {'form': form,  'project': project, 'edit': edit, 'role': instance}, context_instance=RequestContext(request))

def add_edit_role_breadcrumbs(args, kwargs):
    if 'role_id' in kwargs:
        role_id = kwargs['role_id']
        role = get_object_or_404(Role, id=role_id)
        return 'Modify ' + role.name
    else:
        return 'Add a new role'

add_edit_role.breadcrumbs = add_edit_role_breadcrumbs

@login_required
def delete_role(request, project_name,  role_id):
    """Takes in the role id and allows privileged users to delete the role."""

    project = get_object_or_404(CollabProject, slug=project_name)
    project_id = project.id
    role = get_object_or_404(Role, id=role_id)
    
    if not project.admin.filter(id=request.user.id) and not request.user.is_superuser:
        request.user.message_set.create(message="You do not have privileges to delete roles!")
        return HttpResponseRedirect(project.get_absolute_url())
    
    if role.name == 'AnonymousRole':
        request.user.message_set.create(message="You cannot delete the AnonymousRole!")
        return HttpResponseRedirect(project.get_absolute_url())
    
    # If the requested role is of a different project, return to (a) project page.
    if role.project.id != project.id:
        request.user.message_set.create(message="That role does not exist!")
        return HttpResponseRedirect(project.get_absolute_url())
    
    return delete_anything(request, role, 
                           reverse('roles_overview', kwargs={'project_name': project.slug}), 
                           reverse('roles_overview', kwargs={'project_name': project.slug})
                        )
        
delete_role.breadcrumbs = lambda args, kwargs: "Delete %s" % get_object_or_404(Role, id=kwargs['role_id']).name

def member_list(request, *args, **kwargs):
    """Get a list of members of that project"""
    
    project_name = kwargs['project_name']
    project = get_object_or_404(CollabProject, slug=project_name)
    project_id = project.id
    
    if kwargs.get('all'):
        queryset = collab.profiles.models.UserProfile.objects.filter(user__projects__id__exact=project_id).order_by('user__last_name')
    else:
        queryset = collab.profiles.models.UserProfile.objects.filter(user__projects__id__exact=project_id, user__projectmembership__active=True).order_by('user__last_name')
    
    if project.users.filter(id=request.user.id) and request.user.is_active:
        show_contact = True
    else:
        show_contact = False
    
    return collab.profiles.views2.profile_list(request, queryset=queryset, extra_context={'show_contact': show_contact, 'project': project, 'user': request.user})

member_list.breadcrumbs = 'Members'

@login_required
def members_download(request, *args, **kwargs):
    """Get a list of members of that project"""
    
    project_name = kwargs['project_name']
    project = get_object_or_404(CollabProject, slug=project_name)
    project_id = project.id
    
    if not request.user.is_superuser and (request.user not in project.admin.all()):
        return handle_privilege(request, "You do not have privileges to access the member list", '/')
    
    response = HttpResponse(mimetype='text')
    response['Content-Disposition'] = 'attachment; filename='+project.slug+'_memberlist.txt'
    
    members_qs = collab.profiles.models.UserProfile.objects.filter(user__projects__id__exact=project_id).order_by('user__last_name')
    
    member_list = [(member.user.email, member.user.first_name, member.user.last_name) for member in members_qs]
    
    t = loader.get_template('project/all_members.txt')
    c = Context({'members': member_list})
    print t.render(c)
    response.write(t.render(c))
    return response
    

members_download.breadcrumbs = 'Download Member List'

@login_required
def role_bulk_add_remove(request, *args, **kwargs):
    """Allows for bulk adding/removing people to/from roles."""
    
    project_name = kwargs['project_name']
    project = get_object_or_404(CollabProject, slug=project_name)
    id = project.id
    
    task = kwargs['add_or_remove']
    if 'add' in task:
        task = 'add'
    elif 'remove' in task:
        task = 'remove'
    
    # If the user is not the project admin, just return him to the project page. 
    # Note that this may not be good as perhaps he should not have access to the
    # project page.
    if not project.admin.filter(id=request.user.id) and not request.user.is_superuser:
        request.user.message_set.create(message="You do not have privileges to edit roles!")
        return HttpResponseRedirect(project.get_absolute_url())
    
    if request.method == 'POST':
        form = RoleBulkForm(project.id, request.POST)
        if form.is_valid():
            for role in form.cleaned_data['roles']:
                role_members = User.objects.filter(roles=role)
                for user in form.cleaned_data['users']:
                    if 'add' in task:
                        if not role_members.filter(id=user.id):
                            role.users.add(user)
                        message = "Successfully added users to roles."
                    elif 'remove' in task:
                        if role_members.filter(id=user.id):
                            role.users.remove(user)
                        message = "Successfully removed users from roles."
                role.save()
                
            request.user.message_set.create(message=message)
            return HttpResponseRedirect(project.get_absolute_url())
    else:
        form = RoleBulkForm(project.id)
    return render_to_response('project/addtorole.html', {'form': form,  'project': project, 'task': task}, context_instance=RequestContext(request))

def add_edit_role_breadcrumbs(args, kwargs):
    if 'add' in kwargs['add_or_remove']:
        return 'Add users to roles'
    elif 'remove' in kwargs['add_or_remove']:
        return 'Remove users from roles'

role_bulk_add_remove.breadcrumbs = add_edit_role_breadcrumbs

@login_required
def members_bulk_add_remove(request, *args, **kwargs):
    """Allows for bulk adding/removing people to/from projects."""
    
    project_name = kwargs['project_name']
    project = get_object_or_404(CollabProject, slug=project_name)
    id = project.id
    
    project_limit = kwargs.get('project_limit', '')
    
    if project_limit:
        get_object_or_404(CollabProject, slug=project_limit)
    
    task = kwargs['add_or_remove']
    if 'add' in task:
        task = 'add'
    elif 'remove' in task:
        task = 'remove'
    
    # If the user is not the project admin, just return him to the project page. 
    # Note that this may not be good as perhaps he should not have access to the
    # project page.
    if not project.admin.filter(id=request.user.id) and not request.user.is_superuser:
        request.user.message_set.create(message="You do not have privileges to edit roles!")
        return HttpResponseRedirect(project.get_absolute_url())
    
    if request.method == 'POST':
        form = MembersBulkForm(project.id, task, project_limit, request.POST)
        if form.is_valid():
            if 'add' in task:
                for person in form.cleaned_data['users']:
                    p = ProjectMembership(person=person, project=project)
                    p.save()
                    project.default_role.users.add(person)
                message = "Successfully added users to %s" % project.name
            elif 'remove' in task:
                for person in form.cleaned_data['users']:
                    if project.admin.filter(id=person.id) or person.is_superuser:
                        continue # Can't remove an admin from the group.
                    # Need to remove him/her from all roles!
                    for role in person.roles.all():
                        role.users.remove(person)
                    p = ProjectMembership.objects.get(person=person, project=project)
                    p.delete()
                message = "Successfully removed users from %s" % project.name
            project.save()
            
            request.user.message_set.create(message=message)
            return HttpResponseRedirect(reverse('project_members', kwargs={'project_name': project.slug}))
    else:
        form = MembersBulkForm(project.id, task, project_limit)
    return render_to_response('project/add_remove_members.html', {'form': form,  'project': project, 'task': task}, context_instance=RequestContext(request))

def members_bulk_add_remove_breadcrumbs(args, kwargs):
    if 'add' in kwargs['add_or_remove']:
        return 'Add members'
    elif 'remove' in kwargs['add_or_remove']:
        return 'Remove members'

members_bulk_add_remove.breadcrumbs = members_bulk_add_remove_breadcrumbs

@login_required
def roles_overview(request, *args, **kwargs):
    """Shows a summary of the roles"""
    
    project_name = kwargs['project_name']
    project = get_object_or_404(CollabProject, slug=project_name)
    project_id = project.id
    
    # If the user is not the project admin, just return him to the project page. 
    # Note that this may not be good as perhaps he should not have access to the
    # project page.
    if not project.admin.filter(id=request.user.id) and not request.user.is_superuser:
        request.user.message_set.create(message="You do not have privileges to edit roles!")
        return HttpResponseRedirect(project.get_absolute_url())
    
    return render_to_response('project/roles_overview.html', {'project': project, 'user': request.user}, context_instance=RequestContext(request))

roles_overview.breadcrumbs = 'Roles'


@login_required
def add_user(request, *args, **kwargs):
    """Allows a project admin to add a specific user. Also sends an email
    to the added user."""
    
    project_name = kwargs['project_name']
    project = get_object_or_404(CollabProject, slug=project_name)
    project_id = project.id

    # Check if request.user is an admin of this group.
    if not project.admin.filter(id=request.user.id) and not request.user.is_superuser:
        message = "You do not have privileges to add users!"
    else:
        user_to_add = kwargs['userid']
        user_to_add = get_object_or_404(User, username=user_to_add)
        
        # Check if user is already in the group.
        if project.users.filter(id=user_to_add.id):
            message = "User "+user_to_add.username+" is already in this group!"
        else:
            p = ProjectMembership(person=user_to_add, project=project)
            p.save()
            project.default_role.users.add(user_to_add)
            message = "User "+user_to_add.username+" has been added to the group!"
            email_to_user = render_to_string('project/user_added_email.txt', {'project': project}, context_instance=RequestContext(request))
            send_mail('You have been added to '+project.name+'!', email_to_user, CONTACT_FROM_EMAIL, [user_to_add.email])

            email_to_admins = render_to_string('project/user_added_email.txt', {'project': project, 'user': user_to_add}, context_instance=RequestContext(request))
            send_mail(user_to_add.username + ' has been added to ' + project.name, email_to_admins, CONTACT_FROM_EMAIL, [admin.email for admin in project.admin.all()])

    request.user.message_set.create(message=message)
    return HttpResponseRedirect(reverse('project_members', kwargs={'project_name': project.slug}))


add_user.breadcrumbs = 'Add a user'

def subscribe(request, *args, **kwargs):
    """Asks user if he wants to subscribe to a group, and then sends off the request
    to the group admin. If the user is anonymous, let him know he has to subscribe!"""
    
    if request.user.is_anonymous():
        return handle_privilege(request, message="Please register. You need an account to join a collaboration group.", redirect_url=reverse('registration_register'))
    
    project_name = kwargs['project_name']
    project = get_object_or_404(CollabProject, slug=project_name)
    project_id = project.id
    
    # Check if user is already in the group.
    if project.users.filter(id=request.user.id):
        message = "You are already in this group!"
        request.user.message_set.create(message=message)
        return HttpResponseRedirect(project.get_absolute_url())
    
    if request.method == 'POST':
        if "Yes" in request.POST:
            email_to_admin = render_to_string('project/subscribe_request.txt', {'project': project, 'subscriber': request.user}, context_instance=RequestContext(request))
            admin_emails = [admin.email for admin in project.admin.all()]
            send_mail("User "+request.user.username+" wishes to join "+project.name+".", email_to_admin, CONTACT_FROM_EMAIL, admin_emails)
            request.user.message_set.create(message="Your request to join "+project.name+" has been sent. You will be notified if your request is approved.")
        return HttpResponseRedirect(project.get_absolute_url())
    return render_to_response('project/subscribe.html', {'project': project}, context_instance=RequestContext(request))

subscribe.breadcrumbs = lambda args, kwargs: 'Join %s' % get_object_or_404(CollabProject, slug=kwargs['project_name']).name

@login_required
def edit_info(request, *args, **kwargs):
    """Allows the user to edit some basic aspects of the project:
    
    Whether it is active.
    A summary description.
    Any announcements.
    """
    
    project_name = kwargs['project_name']
    project = get_object_or_404(CollabProject, slug=project_name)
    project_id = project.id

    # If the user is not the project admin, just return him to the project page. 
    # Note that this may not be good as perhaps he should not have access to the
    # project page.
    if not project.admin.filter(id=request.user.id) and not request.user.is_superuser:
        request.user.message_set.create(message="You do not have privileges to edit this group!")
        return HttpResponseRedirect(project.get_absolute_url())
    
    if request.user.is_superuser:
        form_class = ProjectInfoAdminsForm
    else:
        form_class = ProjectInfoForm

    if request.method == 'POST':
        form = form_class(request.POST, instance=project)
        if form.is_valid():
            form.save()
            if request.user.is_superuser:
                # Remove admins.
                if "admins_to_remove" in form.cleaned_data:
                    for admin in form.cleaned_data["admins_to_remove"]:
                        p = ProjectMembership.objects.get(person=admin, project=project)
                        p.is_admin = False
                        p.save()
                # Add admins
                if "admins_to_add" in form.cleaned_data:
                    for admin in form.cleaned_data["admins_to_add"]:
                        p = ProjectMembership.objects.get(person=admin, project=project)
                        p.is_admin = True
                        p.save()
            request.user.message_set.create(message="Group information has been updated!")
            return HttpResponseRedirect(project.get_absolute_url())
    else:
        form = form_class(instance=project)
    return render_to_response('project/edit_info.html', {'form': form, 'project':project}, context_instance=RequestContext(request))


edit_info.breadcrumbs = lambda args, kwargs: 'Modify %s' % get_object_or_404(CollabProject, slug=kwargs['project_name']).name

@login_required
def inactivate(request, *args, **kwargs):
    """Allows the admin to mark some members as active/inactive.
    This has nothing to do with the Django User model for being 
    active."""
    
    project_slug = kwargs['project_name']
    project = get_object_or_404(CollabProject, slug=project_slug)
    id = project.id

    task = kwargs['activate_or_inactivate']

    # If the user is not the project admin, just return him to the project page. 
    # Note that this may not be good as perhaps he should not have access to the
    # project page.
    if not project.admin.filter(id=request.user.id) and not request.user.is_superuser:
        request.user.message_set.create(message="You do not have privileges to edit this group!")
        return HttpResponseRedirect(project.get_absolute_url())
    
    if request.method == 'POST':
        form = MembersActiveForm(project.id, task, request.POST)
        if form.is_valid():
            if task=='activate':
                for person in form.cleaned_data['users']:
                    p = ProjectMembership.objects.get(person=person, project=project)
                    p.active = True
                    p.save()
                message = "Successfully activated users." 
            elif task=='inactivate':
                for person in form.cleaned_data['users']:
                    p = ProjectMembership.objects.get(person=person, project=project)
                    p.active = False
                    p.save()
                message = "Successfully de-activated users." 
            request.user.message_set.create(message=message)
            return HttpResponseRedirect(reverse('project_members', kwargs={'project_name': project.slug}))
    else:
        form = MembersActiveForm(project.id, task)
    return render_to_response('project/activity.html', {'form': form,  'project': project, 'task': task}, context_instance=RequestContext(request))

def inactivate_breadcrumbs(args, kwargs):
    if kwargs['activate_or_inactivate']=='activate':
        return 'Activate'
    elif kwargs['activate_or_inactivate']=='inactivate':
        return 'Deactivate'
inactivate.breadcrumbs = inactivate_breadcrumbs
def join_leave_projects(request, *args, **kwargs):
    """A function to allow one to join or leave multiple groups"""
    
    if request.user.is_anonymous():
        return handle_privilege(request, message="In order to join or leave a group you need to be registered and logged in.", redirect_url=reverse('auth_login'))
    
    task = kwargs['join_or_leave']
    if 'join' in task:
        task = 'add'
        nochange = "You did not join any groups."
        template = 'project/join_groups.html'
    elif 'leave' in task:
        task = 'remove'
        nochange = "You did not leave any groups."
        template = 'project/leave_groups.html'
    
    if task=='add':
        numprojects = CollabProject.objects.exclude(users__id=request.user.id).count()
        projects = CollabProject.objects.exclude(users__id=request.user.id)
        if numprojects==0:
            return handle_privilege(request, message="You've joined all the groups there are!", redirect_url=reverse('projects'))
    elif task=='remove':
        numprojects = CollabProject.objects.filter(users__id=request.user.id).count()
        projects = CollabProject.objects.filter(users__id=request.user.id)
        if numprojects==0:
            return handle_privilege(request, message="You're not a member of any group!", redirect_url=reverse('projects'))
    
    if request.method == 'POST':
        form = BulkSubscriptionForm(projects, request.POST)
        if form.is_valid():
            if form.cleaned_data['projects']:
                if task=='add':
                    for project in form.cleaned_data['projects']:
                        email_to_admin = render_to_string('project/subscribe_request.txt', {'project': project, 'subscriber': request.user}, context_instance=RequestContext(request))
                        admin_emails = [admin.email for admin in project.admin.all()]
                        send_mail("User "+request.user.username+" wishes to join "+project.name+".", email_to_admin, CONTACT_FROM_EMAIL, admin_emails)
                        request.user.message_set.create(message="Your request to join "+project.name+" has been sent. You will be notified if your request is approved.")
                elif task=='remove':
                    for project in form.cleaned_data['projects']:
                        for role in request.user.roles.filter(project=project).all():
                            role.users.remove(request.user)
                        p = ProjectMembership.objects.get(person=request.user, project=project)
                        p.delete()
                        request.user.message_set.create(message="Your have been removed from "+project.name+".")
            else:
                request.user.message_set.create(message=nochange)
            return HttpResponseRedirect(reverse('projects'))
    else:
        form = BulkSubscriptionForm(projects)
    return render_to_response(template, {'form': form}, context_instance=RequestContext(request))
def join_leave_projects_breadcrumbs(args, kwargs):
    if kwargs['join_or_leave']=='join':
        return 'Join groups'
    elif kwargs['join_or_leave']=='leave':
        return 'Leave groups'
join_leave_projects.breadcrumbs = join_leave_projects_breadcrumbs

def all_projects(request):
    """View to show all projects. Basically a view wrapped around
    a generic view. This was previously in the urls.py file (sans the 
    view). However,  extra_context has a queryset,  and it would only get
    executed *once*!"""
    
    projects_info = {
                'queryset': CollabProject.objects.all(), 
                'template_object_name': 'projects', 
                'template_name': 'project/projects.html', 
                'extra_context': {'site_info': SiteInfo.objects.all()[:1], 'teleconferences': TeleConference.objects.filter(time__gt=datetime.date.today(), time__lte=(datetime.date.today()+datetime.timedelta(days=7))).order_by('time').all()}
                }
    
    return list_detail.object_list(request, **projects_info)

all_projects.breadcrumbs = 'All Groups'

def create_project(request):
    """View to create a new project.
    In the past I just linked to the page in the admin, but that
    doesn't automatically create users and admins for you.
    And it may be a pain to create project memberships manually.
    
    Perhaps the Django admin is customizable enough to fix this,  
    but for now I'll just code it myself. At least this way I can make sure 
    no one (but me) makes any major errors and destroys the site
    
    First check if the user is a superuser..."""
    
    if not request.user.is_superuser:
        return handle_privilege(request, "Only the site administrator can create a new project!", '/')
    
    if request.method == 'POST':
        form = CreateProjectForm(request.POST)
        if form.is_valid():
            newproject = CollabProject()
            newproject = form.save(commit=False)
            newproject.start_date = datetime.date.today()
            newproject.save()
            form.save_m2m()
            for admin in form.cleaned_data["admins"]:
                p = ProjectMembership(person=admin, project=newproject, is_admin=True)
                p.save()
            return handle_privilege(request, 'The collaboration group "'+newproject.name+'" has been created!', reverse('project_summary', args=[newproject.slug]))
    else:
        form = CreateProjectForm()
    return render_to_response('project/create_project.html', { 'form': form }, context_instance=RequestContext(request))
create_project.breadcrumbs = 'Create a new group'

def members_add_filter(request, *args, **kwargs):
    """A simple view that shows all groups except the
    current one. Each link is then to add members
    only from a certain group."""
    
    project_name = kwargs['project_name']
    project = get_object_or_404(CollabProject, slug=project_name)
    project_id = project.id
    
    queryset = CollabProject.objects.exclude(id=project_id)

    return render_to_response('project/group_select.html', {'projects': queryset, 'project': project, }, context_instance=RequestContext(request))

members_add_filter.breadcrumbs = 'Limit members to a certain group'

def documentation(request, *args, **kwargs):
    """View to show any documentation related to a project."""
    
    project_name = kwargs['project_name']
    project = get_object_or_404(CollabProject, slug=project_name)
    project_id = project.id

    if not is_allowed(request, project_id, 'documentation', 'Viewable'):
        return handle_privilege(request, "You do not have privileges to view the documentation section!", project.get_absolute_url())

    if is_allowed(request, project_id, 'documentation', 'Editable'):
        edit = True
    else:
        edit = False

    return render_to_response('project/documentation.html', {'project': project, 'editable': edit}, context_instance=RequestContext(request))

documentation.breadcrumbs = 'Documentation'

@login_required
def edit_doc(request, *args, **kwargs):
    """View to edit documentation."""
    
    project_name = kwargs['project_name']
    project = get_object_or_404(CollabProject, slug=project_name)
    project_id = project.id

    if not is_allowed(request, project_id, 'documentation', 'Editable'):
        return handle_privilege(request, "You do not have privileges to edit the documentation section!", project.get_absolute_url())
    
    view_dict = {
                 'form_class': DocumentationForm, 
                 'object_id': project_id, 
                 'post_save_redirect': reverse('documentation', kwargs={'project_name': project_name}), 
                 'login_required': True, 
                 'template_name': 'project/doc_edit.html', 
                 'extra_context': {'project': project}, 
                }
    
    return create_update.update_object(request, **view_dict)

edit_doc.breadcrumbs = 'Modify Documentation'

@login_required
def edit_announcement(request, *args, **kwargs):
    """View for editing announcements"""
    
    project_name = kwargs['project_name']
    project = get_object_or_404(CollabProject, slug=project_name)
    project_id = project.id

    if not is_allowed(request, project_id, 'announcements', 'Editable'):
        return handle_privilege(request, "You do not have privileges to edit announcements!", project.get_absolute_url())
    
    anonymous = Role.objects.get(project=project, name="AnonymousRole")
    if not anonymous.privileges.filter(permission_type='Viewable', related_model='announcements'.lower()):
        announce_warning = True
    else:
        announce_warning = False
    
    print announce_warning
    view_dict = {
                 'form_class': AnnouncementForm, 
                 'object_id': project_id, 
                 'post_save_redirect': project.get_absolute_url(), 
                 'login_required': True, 
                 'template_name': 'project/edit_announce.html', 
                 'extra_context': {'project': project, 'announce_warning': announce_warning}, 
                }
    
    return create_update.update_object(request, **view_dict)

edit_announcement.breadcrumbs = 'Modify Announcements'

def about(request):
    """
    An about page. The about information is stored in the SiteInfo
    model.

    Also, it shows certain statistics (number of groups, etc).
    """

    overview = SiteInfo.objects.all()[0].overview

    statistics = {'num_groups': CollabProject.objects.count(),
                  'num_users': User.objects.count()
                  }

    # Get number of emails by TLD
    emails = (person.email for person in User.objects.all())
    tld_stats = {}
    for email in emails:
        tld = email[email.rfind('.'):]
        tld_stats[tld] = tld_stats.setdefault(tld, 0) + 1
    statistics['email_stats'] = tld_stats
    
    return render_to_response('siteinfo/overview.html', {'overview': overview, 'stats': statistics}, context_instance=RequestContext(request))

about.breadcrumbs = 'About'
