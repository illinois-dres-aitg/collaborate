"""Most of the views on this page are modified versions of those
in the original django-profiles package"""


from django.contrib.auth.decorators import login_required
from forms import ProfileForm, PasswordReset, ContactUserForm
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.models import User
from models import UserProfile
from utils import get_profile_model
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.views.generic.list_detail import object_list
from django.core.mail import send_mail
from collab.settings import CONTACT_FROM_EMAIL
from collab.project.models import CollabProject

def create_profile(request, form_class=None, success_url=None,
                   template_name='profiles/create_profile.html'):
    """
    Create a profile for the user, if one doesn't already exist.
    Borrowed from django-profile.
    
    If the user already has a profile, as determined by
    ``request.user.get_profile()``, a redirect will be issued to the
    :view:`profiles.views.edit_profile` view. If no profile model has
    been specified in the ``AUTH_PROFILE_MODULE`` setting,
    ``django.contrib.auth.models.SiteProfileNotAvailable`` will be
    raised.
    
    To specify the form class used for profile creation, pass it as
    the keyword argument ``form_class``; if this is not supplied, it
    will fall back to ``form_for_model`` for the model specified in
    the ``AUTH_PROFILE_MODULE`` setting.
    
    If you are supplying your own form class, it must define a method
    named ``save()`` which corresponds to the signature of ``save()``
    on ``form_for_model``, because this view will call it with
    ``commit=False`` and then fill in the relationship to the user
    (which must be via a field on the profile model named ``user``, a
    requirement already imposed by ``User.get_profile()``) before
    finally saving the profile object. If many-to-many relations are
    involved, the convention established by ``form_for_model`` of
    looking for a ``save_m2m()`` method on the form is used, and so
    your form class should define this method.
    
    To specify a URL to redirect to after successful profile creation,
    pass it as the keyword argument ``success_url``; this will default
    to the URL of the :view:`profiles.views.profile_detail` view for
    the new profile if unspecified.
    
    To specify the template to use, pass it as the keyword argument
    ``template_name``; this will default to
    :template:`profiles/create_profile.html` if unspecified.
    
    Context:
    
        form
            The profile-creation form.
    
    Template:
    
        ``template_name`` keyword argument, or
        :template:`profiles/create_profile.html`.
    
    """
    try:
        profile_obj = request.user.get_profile()
        return HttpResponseRedirect(reverse('profiles_edit_profile'))
    except ObjectDoesNotExist:
        pass
    profile_model = get_profile_model()
    if success_url is None:
        success_url = reverse('profiles_profile_detail',
                              kwargs={ 'username': request.user.username })
    if form_class is None:
        form_class = ProfileForm
        initial = {'user': request.user, 'email': request.user.email}
    if request.method == 'POST':
        form = form_class(request.user, request.POST)
        if form.is_valid():
            profile_obj = UserProfile()
            profile_obj = form.save(commit=False)
            profile_obj.user = request.user
            profile_obj.save()
            if hasattr(form, 'save_m2m'):
                form.save_m2m()
            return HttpResponseRedirect(success_url)
    else:
        form = form_class(request.user, initial=initial)
    return render_to_response(template_name,
                              { 'form': form },
                              context_instance=RequestContext(request))
create_profile = login_required(create_profile)
create_profile.breadcrumbs = "Create Profile"

def get_initial_data(profile_obj):
    """
    Given a user profile object, returns a dictionary representing its
    fields, suitable for passing as the initial data of a form.
    
    """
    opts = profile_obj._meta
    data_dict = {}
    for f in opts.fields + opts.many_to_many:
        data_dict[f.name] = f.value_from_object(profile_obj)
    return data_dict

def edit_profile(request, username=None, form_class=None, success_url=None,
                 template_name='profiles/edit_profile.html'):
    """
    Edit a user's profile.
    
    If the user does not already have a profile (as determined by
    ``User.get_profile()``), a redirect will be issued to the
    :view:`profiles.views.create_profile` view; if no profile model
    has been specified in the ``AUTH_PROFILE_MODULE`` setting,
    ``django.contrib.auth.models.SiteProfileNotAvailable`` will be
    raised.
    
    To specify the form class used for profile editing, pass it as the
    keyword argument ``form_class``; this form class must have a
    ``save()`` method which will save updates to the profile
    object. If not supplied, this will default to
    ``form_for_instance`` for the user's existing profile object.
    
    To specify the URL to redirect to following a successful edit,
    pass it as the keyword argument ``success_url``; this will default
    to the URL of the :view:`profiles.views.profile_detail` view if
    not supplied.
    
    To specify the template to use, pass it as the keyword argument
    ``template_name``; this will default to
    :template:`profiles/edit_profile.html` if not supplied.
    
    Context:
    
        form
            The form for editing the profile.
        
        profile
            The user's current profile.
    
    Template:
    
        ``template_name`` keyword argument or
        :template:`profiles/edit_profile.html`.
    
    """
    if username == None:
        user = request.user
    else:
        user = User.objects.get(username=username)
        # Again, commenting out code allowing group admins from editing profiles
        # and only allowing the user and the superuser to do it.
        if not request.user.is_superuser:
            request.user.message_set.create(message="You do not have privileges to edit that profile!")
            return HttpResponseRedirect('/')

#        common_projects = CollabProject.objects.filter(users__id=user.id) & CollabProject.objects.filter(users__id=request.user.id, projectmembership__is_admin=True)
#        if not common_projects:
##        user_projects = user.projects.all()
##        if not [True for project in user_projects if ((request.user.is_superuser) or (request.user in project.admin.all()))]:
#            request.user.message_set.create(message="You do not have privileges to edit that profile!")
#            return HttpResponseRedirect('/')

    try:
        profile_obj = user.get_profile()
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse('profiles_create_profile'))
    if success_url is None:
        success_url = reverse('profiles_profile_detail',
                              kwargs={ 'username': user.username })
    if form_class is None:
        form_class = ProfileForm
        A = {'user': user, 'email': user.email, 'first_name': user.first_name, 'last_name': user.last_name}
        initial = get_initial_data(profile_obj)
        initial.update(A)
        del initial['id']
    if request.method == 'POST':
        form = form_class(user, request.POST, instance=profile_obj)
        if form.is_valid():
            profile_obj = form.save(commit=False)
            profile_obj.user = user
            profile_obj.save()
            if hasattr(form, 'save_m2m'):
                form.save_m2m()
            return HttpResponseRedirect(success_url)
    else:
        form = form_class(request.user, initial, instance=profile_obj)
    return render_to_response(template_name,
                              { 'form': form,
                                'profile': profile_obj,
                                'username': user.username },
                              context_instance=RequestContext(request))
edit_profile = login_required(edit_profile)
edit_profile.breadcrumbs = 'Modify Profile'

def profile_list(request, public_profile_field=None,
                 template_name='profiles/profile_list.html', **kwargs):
    """
    List of user profiles.
    
    If no profile model has been specified in the
    ``AUTH_PROFILE_MODULE`` setting,
    ``django.contrib.auth.models.SiteProfileNotAvailable`` will be
    raised.
    
    If a field on the profile model determines whether the profile can
    be publicly viewed, pass the name of that field as the keyword
    argument ``public_profile_field``; the ``QuerySet`` of profiles
    will be filtered to include only those on which that field is
    ``True`` (as a result, this field must be a ``BooleanField``).
    
    This view is a wrapper around the
    :view:`django.views.generic.list_detail.object_list` generic view,
    so any arguments which are legal for that view will be accepted,
    with the exception of ``queryset``, which will always be set to
    the default ``QuerySet`` of the profile model, optionally filtered
    as described above.
    
    Template:
    
        ``template_name`` keyword argument or
        :template:`profiles/profile_list.html`.
    
    Context:
    
        Same as the :view:`django.views.generic.list_detail.object_list`
        generic view.
    
    """
    profile_model = get_profile_model()
    queryset = profile_model._default_manager.all()
    if 'queryset' in kwargs:
        queryset = queryset & kwargs['queryset']
        del kwargs['queryset']
#    if public_profile_field is not None:
#        queryset = queryset.filter(**{ public_profile_field: True })
    return object_list(request,
                       queryset=queryset,
                       template_name=template_name,
                       **kwargs)

#@login_required
#def pass_change(request):
#    """Allows the user to change the password"""
#    
#    if request.method == 'POST':
#        form = PasswordReset(request.user,  request.POST)
#        if form.is_valid():
#            request.user.set_password(form.cleaned_data['password1'])
#            request.user.save()
#            request.user.message_set.create(message="Your password has been changed")
#            return HttpResponseRedirect(request.user.profile.all()[0].get_absolute_url())
#    else:
#        form = PasswordReset(request.user)
#    return render_to_response('profiles/password_change.html', {'form': form  }, context_instance=RequestContext(request))

@login_required
def contact_user(request, username):
    """Allows a logged in user to contact another user. Both users must share a 
    group/project."""
    
    contacted = get_object_or_404(User, username=username)
    contacter = request.user
    
#    contactable = False
    
#    print CollabProject.objects.filter(
#    print contacted.projects.objects.all() & request.user.projects.objects.all()
    
    contacted_projects = contacted.projects.all()
    contacter_projects = request.user.projects.all()
    
    contactable = False
    for project in contacted_projects:
        if project in contacter_projects:
            contactable = True
            break
    
    if not request.user.is_active:
        contactable = False
    
    if not contactable:
        request.user.message_set.create(message="You cannot contact this user!")
        return HttpResponseRedirect(contacted.profile.all()[0].get_absolute_url())
    
    if request.method == 'POST':
        form = ContactUserForm(request.POST)
        if form.is_valid():
            email_message = form.cleaned_data['email_message']
            body = "You have received a message from " + contacter.first_name + ' ' + contacter.last_name + " (" + contacter.username + "). \n\n Email: " + contacter.email + "\n Message: \n\n" + email_message
            subject = "Message from iCita!"
            email_list = [contacted.email]
            from_email = CONTACT_FROM_EMAIL
            send_mail(subject, body, from_email, email_list, fail_silently=False)
            request.user.message_set.create(message="Your message has been sent to "+contacted.first_name+' '+contacted.last_name)
            return HttpResponseRedirect('/')
    else:
        form = ContactUserForm()
    return render_to_response('profiles/contact.html', {'form': form, 'contacted': contacted}, context_instance=RequestContext(request))


    
contact_user.breadcrumbs = lambda args, kwargs: 'Contact %s' % kwargs['username']
