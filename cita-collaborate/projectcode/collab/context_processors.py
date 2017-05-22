from django.contrib.sites.models import Site
import collab.settings as settings
import re
from django.shortcuts import get_object_or_404
from collab.project.models import CollabProject
import collab.breadcrumbs as bc
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape as escape
from collab.helpers import is_allowed
from django.utils.http import urlquote
from django.contrib.auth import REDIRECT_FIELD_NAME
from collab.siteinfo.models import SiteInfo
from django.core.urlresolvers import reverse

def root_url(request):
    current_site = Site.objects.get(id=settings.SITE_ID)
    return {'SITE_URL': current_site.domain, 'MEDIA_URL': settings.MEDIA_URL}

def message_to_anonymous(request):
    """Pass any messages to anonymous users. This function
    will only send one message per request..."""
    return {'ANONYMOUS_MESSAGE': request.session.get('message_anonymous')}

def add_subscribe_menu(request):
    """Checks to see if the user is viewing a project,  and is logged in, 
    and is not a member of that project. If so,  he/she will see a link 
    that allows him/her to request the project admin to be a member."""

    url = request.path_info
    pattern = re.compile('^/groups?/([\w-]+)')
    results = pattern.findall(url)
    if results:
        project = get_object_or_404(CollabProject, slug=results[0])
        if project.users.filter(id=request.user.id):
            return {}
        else:
            # User is logged in, authenticated, but not part of this group.
            return {'subscribe_menu': True}
    return {}

def bc_join_callback(breadcrumbs):
    """Function for converting the breadcrumbs list
    into an HTML string ready for placement into the
    template."""
    
#    return mark_safe(u'<ul class="breadcrumbs"><li class="first_item">%s </li></ul>' % "</li><li class=\"breadcrumbs\">".join(breadcrumbs[2:]))
    return mark_safe(u'<li class="first_item">%s </li>' % "</li><li class=\"breadcrumbs\">".join(breadcrumbs[2:]))
#    return mark_safe(u'<ul class="breadcrumbs"><li class="breadcrumbs">%s</li></ul>' % "</li><li class=\"breadcrumbs\">".join(breadcrumbs[2:]))

def breadcrumbs(request):
    """For adding breadcrumbs to pages"""
    
    breadcrumbs, default_title = bc.get_breadcrumbs(request, join_callback=bc_join_callback)
    
    if breadcrumbs:
        return {'breadcrumbs': breadcrumbs}
    else:
        return {}

def announce_privilege(request):
    """Checks to see if the user has privileges to view announcements."""
    
    context = {'announce_view': True}
    url = request.path_info
    pattern = re.compile('^/groups?/([\w-]+)')
    results = pattern.findall(url)
    if results:
        project = get_object_or_404(CollabProject, slug=results[0])
        if not is_allowed(request, project.id, 'Announcements', 'Viewable'):
            context['announce_view'] = False
    return context

def announce_expired(request):
    """Checks to see if the announcement has expired."""
    
    context = {'announce_expired': False}
    url = request.path_info
    pattern = re.compile('^/groups?/([\w-]+)')
    results = pattern.findall(url)
    if results:
        import datetime
        project = get_object_or_404(CollabProject, slug=results[0])
        if project.announcements and project.announce_expire and project.announce_expire <= datetime.date.today():
            context['announce_expired'] = True
    return context


def menu_privileges(request):
    """This controls some of the items that appear in the project menu"""
    
    url = request.path_info
    pattern = re.compile('^/groups?/([\w-]+)')
    results = pattern.findall(url)
    if results:
        project = get_object_or_404(CollabProject, slug=results[0])
    else:
        return {}

    priv_keys = ['teleconference', 'documentation', 'issuel', 'action', 'announcements']
    privileges = ['teleconference', 'documentation', 'issue list', 'action item', 'announcements']
    allowed = dict([(k, is_allowed(request, project.id, p, 'Viewable') or is_allowed(request, project.id, p, 'Editable')) for (k, p) in zip(priv_keys, privileges)])
    context = {'menu_allowed': allowed}
    return context

    
def time_zone(request):
    """Adds the user's preferred time zone to the context. Null if no
    time zone or anonymous user."""

    if request.user.is_anonymous():
        return {'time_zone': None}
    else:
        if request.user.profile.all():
            return {'time_zone': request.user.profile.all()[0].time_zone}
        else:
            return {'time_zone': None}
            
def login_url_with_redirect(request):
    """
    This context processor redirects the user to the page he was in
    prior to logging in.
    """
    
    login_url = settings.LOGIN_URL
    path = urlquote(request.get_full_path())

    # There should be no redirect if the person is at the log in or the
    # log out page when he tries to log in.
    if (path != settings.LOGOUT_URL) and (path != settings.LOGIN_URL) and (path != reverse('password_reset_complete')) and (path != '/'):
        url = '%s?%s=%s' % (settings.LOGIN_URL, REDIRECT_FIELD_NAME, path)
    else:
        url = settings.LOGIN_URL
    return {'login_url': url}

def site_announcements(request):
    """
    This context processor will check if there is a sitewide
    announcement, and if there is, will add it to the context.
    """

    site_info = SiteInfo.objects.all()[:1]
    if site_info[0].announcements:
        return {'site_announcements': site_info[0].announcements}
    else:
        return {}


def add_year(request):
    """
    Context processor to add the year to the template (for
    copyright...).
    """
    import datetime
    return {'copyright_year': datetime.datetime.now().year}
