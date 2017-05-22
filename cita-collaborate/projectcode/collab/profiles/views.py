"""
Views for creating, editing and viewing site-specific user profiles.

"""

from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.views.generic.list_detail import object_list

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from utils import get_profile_model
from collab.project.models import CollabProject


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


@login_required
def profile_detail(request, username, public_profile_field=None,
                   template_name='profiles/profile_detail.html'):
    """
    Detail view of a user's profile.
    
    If no profile model has been specified in the
    ``AUTH_PROFILE_MODULE`` setting,
    ``django.contrib.auth.models.SiteProfileNotAvailable`` will be
    raised.

    If the user has not yet created a profile, ``Http404`` will be
    raised.

    If a field on the profile model determines whether the profile can
    be publicly viewed, pass the name of that field as the keyword
    argument ``public_profile_field``; that attribute will be checked
    before displaying the profile, and if it does not return a
    ``True`` value, the ``profile`` variable in the template will be
    ``None``. As a result, this field must be a ``BooleanField``.
    
    To specify the template to use, pass it as the keyword argument
    ``template_name``; this will default to
    :template:`profiles/profile_detail.html` if not supplied.
    
    Context:
    
        profile
            The user's profile, or ``None`` if the user's profile is
            not publicly viewable (see the note about
            ``public_profile_field`` above).
    
    Template:
    
        ``template_name`` keyword argument or
        :template:`profiles/profile_detail.html`.
    
    """
    user = get_object_or_404(User, username=username)
    try:
        profile_obj = user.get_profile()
    except ObjectDoesNotExist:
        raise Http404
    if public_profile_field is not None and \
       not getattr(profile_obj, public_profile_field):
        profile_obj = None
    
    # Check for permissions. 
    viewable = False
    admin = False
    if request.user == user:
        # If the logged in user is the same as that of the profile,
        # he/she can see the confidential material.
        viewable = True
    elif request.user.is_superuser:
        viewable = True
        admin = True
    else:
        view_conf = False
        # Commenting out the below because of a security risk.
        # If I'm an admin and I want to see the details of a profile of 
        # someone in an other group, I merely have to add her/him
        # to my group and I can then see it. 
        # So right now I'm setting it so that only the superuser and the
        # user h(im|er)self can view it.
        
#        if request.user.is_authenticated():
#            # If request.user is an admin of a project that user is a member of,
#            # then he/she can see the confidential material.
#            common_projects = CollabProject.objects.filter(users__id=user.id) & CollabProject.objects.filter(users__id=request.user.id, projectmembership__is_admin=True)
#            if common_projects:
#                viewable = True
#                admin = True
    
    if not viewable:
        request.user.message_set.create(message="You do not have privileges to view that profile.")
        return HttpResponseRedirect('/')

    
    return render_to_response(template_name,
                              {'profile': profile_obj, 'user_is_admin': admin},
                              context_instance=RequestContext(request))

profile_detail.breadcrumbs = lambda args, kwargs: "%s Profile" % kwargs['username']

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
    if 'queryset' in kwargs:
        del kwargs['queryset']
    queryset = profile_model._default_manager.all()
    if public_profile_field is not None:
        queryset = queryset.filter(**{ public_profile_field: True })
    return object_list(request,
                       queryset=queryset,
                       template_name=template_name,
                       **kwargs)
