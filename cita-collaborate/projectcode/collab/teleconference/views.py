from forms import TeleConferenceForm,  MinutesForm
from models import TeleConference, Minutes
from collab.project.models import CollabProject,  Privilege,  Role
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.generic import list_detail
from django.contrib.auth.models import User
import datetime
from collab.helpers import is_allowed, handle_privilege, delete_anything
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from collab.timezoneinfo import construct_timezones
from collab.action.models import ActionItem

@login_required
def add_edit_tele(request,  **kwargs):
    """Takes in the project id and (if editing) the tele_id and allows you to add a new teleconference or edit an old one."""

    project_name = kwargs['project_name']
    project = get_object_or_404(CollabProject, slug=project_name)
    project_id = project.id
    
    if not is_allowed(request,  project_id,  TeleConference._meta.verbose_name,  'Editable'):
        return handle_privilege(request, "You do not have privileges to edit teleconferences!", project.get_absolute_url())
    
    if 'tele_id' in kwargs:
        tele_id = kwargs['tele_id']
        teleconference = get_object_or_404(TeleConference, id=tele_id)
        # Check if the teleconference exists in that project!
        if teleconference.project.id != int(project_id):
            return handle_privilege(request, "That teleconference does not exist in this project!", project.get_absolute_url())
        edit = True
        instance = teleconference
        initial = {'date': teleconference.time, 'time': teleconference.time, 'duration': teleconference.duration}
    else:
        edit = False
        instance = None
        initial = {}

    action_text = None
    see_action = False
    last_tele = {}

    if request.method == 'POST':
        form = TeleConferenceForm(project.id,  request.POST,  instance=instance, initial=initial)
        if form.is_valid():
            if not edit:
                tele = TeleConference()
                message = "Teleconference added!"
            else:
                message = "Teleconference modified!"
            tele = form.save(commit=False)
            tele.project = project
            tele.duration = form.cleaned_data['duration']
            date = form.cleaned_data['date']
            time = form.cleaned_data['time'][0]
            tz = form.cleaned_data['time'][1]
            tzs = construct_timezones(date.year)
            if tz=='Pacific':
                tz = tzs[0]
            elif tz=='Mountain':
                tz = tzs[1]
            elif tz=='Central':
                tz = tzs[2]
            elif tz=='Eastern':
                tz = tzs[3]
            elif tz=='UTC':
                tz = tzs[4]
            dt = datetime.datetime(year=date.year, month=date.month, day=date.day, hour=time.hour, minute=time.minute, tzinfo=tz)
            dt = dt.astimezone(tzs[2])  # Convert to Central
            dt = datetime.datetime.combine(dt.date(), dt.time())  # Convert to timezone-agnostic (MySQL can't handle them)
            tele.time = dt
            tele.save()
            request.user.message_set.create(message=message)
            return HttpResponseRedirect(reverse('tele_details', kwargs={'project_name': project.slug, 'tele_id': tele.id}))
    else:
	# Get action items to be placed in agenda, if desired.
	if is_allowed(request, project_id, ActionItem._meta.verbose_name, 'Viewable'):
	    see_action = True
	    action_items = ActionItem.objects.filter(project=project, status="Open").all()
	    if action_items:
		action_text = "\\n* " + "\\n* ".join([action.action for action in action_items])

	# Get the most recent (completed) teleconference.
	queryset = TeleConference.objects.filter(project=project, time__lte=datetime.datetime.now()).order_by('-time')
	if queryset.count():
	    prev_tele = queryset.all()[0]
	    if prev_tele:
		last_tele['agenda'] = prev_tele.agenda.replace('\r\n', '\\n')
		last_tele['location'] = prev_tele.location
		last_tele['number'] = prev_tele.phone
		last_tele['password'] = prev_tele.phone_code
		last_tele['url'] = prev_tele.online_uri
		last_tele['userid'] = prev_tele.online_userid
		last_tele['opassword'] = prev_tele.online_password
		last_tele['instructions'] = prev_tele.online_instructions.replace('\r\n', '\\n')
		last_tele['other_instructions'] = prev_tele.other_instructions.replace('\r\n', '\\n')
		last_tele['notes'] = prev_tele.notes.replace('\r\n', '\\n')
		last_tele['time_h'] = prev_tele.time.hour
		last_tele['time_m'] = prev_tele.time.minute
		if prev_tele.duration:
		    last_tele['duration_h'] = prev_tele.duration.hour
		    last_tele['duration_m'] = prev_tele.duration.minute
		# Check if there have been two previous teleconferences. If
		# there have, calculate the difference in time between the
		# two, and use that as an estimate for the next
		# teleconference. Otherwise, jut add a week to the last one.
		if queryset.count() > 1:
		    second_last_tele = queryset.all()[1]
		    difference = prev_tele.time - second_last_tele.time
		    next_tele_date = prev_tele.time + difference
		else:
		    next_tele_date = prev_tele.time + datetime.timedelta(7)
		last_tele['year'] = next_tele_date.year
		last_tele['month'] = next_tele_date.strftime('%B')
		last_tele['day'] = next_tele_date.day


        # See bug 51 for why I pass in the project id.
        form = TeleConferenceForm(project.id,  instance=instance, initial=initial)
    return render_to_response('teleconference/addtele.html', {'form': form, 'edit': edit, 'project': project, 'teleconference': instance, 'action_text': action_text, 'see_action': see_action, 'last_tele': last_tele}, context_instance=RequestContext(request))

def add_edit_tele_breadcrumbs(args, kwargs):
    if 'tele_id' in kwargs:
        return 'Modify teleconference'
    else:
        return 'Add a teleconference'
add_edit_tele.breadcrumbs = add_edit_tele_breadcrumbs

def details(request, project_name,  tele_id,  *args,  **kwargs):
    """Takes in the teleconference id and shows its details. If the user has permissions, it will allow him/her to delete the teleconference as well."""

    project = get_object_or_404(CollabProject, slug=project_name)
    project_id = project.id
    teleconference = get_object_or_404(TeleConference, id=tele_id)

    # If the requested teleconference is of a different project, return to (a) project page.
    if teleconference.project.id != project.id:
        return handle_privilege(request, "That teleconference does not exist!", project.get_absolute_url())

    if not is_allowed(request,  project_id,  TeleConference._meta.verbose_name,  'Viewable'):
        return handle_privilege(request, "You do not have privileges to view teleconferences!", project.get_absolute_url())

    if is_allowed(request,  project_id,  TeleConference._meta.verbose_name,  'Editable'): 
        deletable = True
    else:
        deletable = False

    if is_allowed(request,  project_id,  Minutes._meta.verbose_name,  'Editable'):
        edit_minutes = True
    else:
        edit_minutes = False
    
    # Take the string of other participants, and create a list out of them (comma separated string)
    try:
        other_participants = [S.strip() for S in teleconference.minutes.other_participants.split(',')]
        # Silly hack below. If minutes.other_participants exists but is empty, then a list with an 
        # empty string gets passed. Need to set that to None. 
        other_participants = [S for S in other_participants if S != u'']
    except Minutes.DoesNotExist:
        other_participants = None
    
    return render_to_response('teleconference/teledetails.html', {'teleconference': teleconference,  'deletable': deletable,  'edit_minutes': edit_minutes,  'project': project, 'other_participants': other_participants}, context_instance=RequestContext(request))

details.breadcrumbs = 'Details'

def all_teleconferences(request, project_name):
    """Takes in the the project id and shows all teleconferences (upcoming and archived)."""

    project = get_object_or_404(CollabProject, slug=project_name)
    project_id = project.id
    
    if not is_allowed(request,  project_id,  TeleConference._meta.verbose_name,  'Viewable'):
        return handle_privilege(request, "You do not have privileges to view teleconferences!", project.get_absolute_url())

    if is_allowed(request,  project_id,  TeleConference._meta.verbose_name,  'Editable'):
        editable = True
    else:
        editable = False

    teleconferences_list = {
                          'queryset': TeleConference.objects.filter(project__id=project_id).filter(time__gte=datetime.date.today()).order_by('time'),   
                          'template_name': 'teleconference/alltele.html', 
                          'template_object_name': 'upcoming_tele', 
                          'extra_context': {'past_tele': TeleConference.objects.filter(project__id=project_id).filter(time__lt=datetime.date.today()).order_by('-time'),  'project': project, 'editable': editable}, 
                        }
    
    return list_detail.object_list(request,  **teleconferences_list)

all_teleconferences.breadcrumbs = 'Teleconferences'

@login_required
def delete_tele(request, project_name,  tele_id):
    """Takes in the teleconference id and allows user with privileges to delete the teleconference."""

    project = get_object_or_404(CollabProject, slug=project_name)
    project_id = project.id
    teleconference = get_object_or_404(TeleConference, id=tele_id)
    
    
    if not is_allowed(request,  project_id,  TeleConference._meta.verbose_name,  'Editable'):
        return handle_privilege(request, "You do not have privileges to edit teleconferences!", project.get_absolute_url())
    
    # If the requested teleconference is of a different project, return to (a) project page.
    if teleconference.project.id != project.id:
        return handle_privilege(request, "That teleconference does not exist!", project.get_absolute_url())
    
    return delete_anything(request, teleconference, 
                            reverse('tele_overview', kwargs={'project_name': teleconference.project.slug}), 
                            reverse('tele_details', kwargs={'project_name': teleconference.project.slug, 'tele_id': teleconference.id}))

delete_tele.breadcrumbs = 'Delete'
#    
#    if request.method == 'POST':
#        form = DeleteForm(request.POST)
#        if "Yes" in request.POST:
#            teleconference.delete()
#            message = "The teleconference was deleted."
#            return handle_privilege(request, message, reverse('tele_overview', kwargs={'project_name': teleconference.project.slug}))
#        else:
#            message = "The teleconference was not deleted."
#            return handle_privilege(request, message, reverse('tele_details', kwargs={'project_name': teleconference.project.slug, 'tele_id': teleconference.id}))
#    else:
#        form = DeleteForm()
#    return render_to_response('delete.html', {'form': form,  'description': 'this teleconference', 'project': project}, context_instance=RequestContext(request))

@login_required
def add_edit_minutes(request,  **kwargs):
    """Takes in the project id and tele_id and allows you to edit/add the minutes for the relevant teleconference."""

    project_name = kwargs['project_name']
    project = get_object_or_404(CollabProject, slug=project_name)
    project_id = project.id
    
    tele_id = kwargs['tele_id']
    teleconference = get_object_or_404(TeleConference, id=tele_id)

    if not is_allowed(request,  project_id,  Minutes._meta.verbose_name,  'Editable'):
        return handle_privilege(request, "You do not have privileges to edit the minutes!", teleconference.get_absolute_url())
    
    # Check if the teleconference exists in that project!
    if teleconference.project.id != project.id:
        return handle_privilege(request, "That teleconference does not exist!", project.get_absolute_url())
    
    try:
        teleconference.minutes
        # The minutes already exist, so we are actually editing them now
        edit = True
        instance = teleconference.minutes
        initial = {'other_participants': teleconference.minutes.other_participants}
    except Minutes.DoesNotExist:
        edit = False
        instance = None
        initial = None
    
    if request.method == 'POST':
        form = MinutesForm(teleconference.id,  request.POST,  instance=instance, initial=initial)
        if form.is_valid():
            if not edit:
                minutes = Minutes()
                message = "Minutes added!"
            else:
                message = "Minutes modified!"
            minutes = form.save(commit=False)
            minutes.teleconference = teleconference
            minutes.other_participants = form.cleaned_data['other_participants']
            minutes.save()
            form.save_m2m()
            request.user.message_set.create(message=message)
            print teleconference.get_absolute_url()
            return HttpResponseRedirect(teleconference.get_absolute_url())
    else:
        form = MinutesForm(teleconference.id,  instance=instance, initial=initial)
        print form.fields['other_participants'].help_text
    return render_to_response('teleconference/add_edit_minutes.html', {'form': form,  'edit': edit,  'project': project}, context_instance=RequestContext(request))
    
add_edit_minutes.breadcrumbs = 'Modify minutes'

def global_teleconferences(request):
    """View wrapper for generic object list view.
    Shows all teleconferences scheduled in the future."""
    
    teleconferences_list = {
                          'queryset': TeleConference.objects.filter(time__gte=datetime.date.today()).order_by('time'),   
                          'template_name': 'teleconference/global_alltele.html', 
                          'template_object_name': 'upcoming_tele', 
                        }
    
    return list_detail.object_list(request, **teleconferences_list)

global_teleconferences.breadcrumbs = 'All Teleconferences'
