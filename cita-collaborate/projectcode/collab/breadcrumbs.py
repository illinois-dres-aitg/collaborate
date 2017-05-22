# http://www.djangosnippets.org/snippets/1026/

# Python
from urlparse import urljoin

# Django
from django import http
from django.core import urlresolvers
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.http import urlquote
from django.utils.html import conditional_escape as escape
from django.utils.safestring import mark_safe

def join(str, mylist):
    str=escape(str)
    return mark_safe(str.join([escape(item) for item in mylist]))

'''
Simple Breadcrumbs for Django:

The value of request.path gets examined and all views of the 'upper' urls
need to have an attribute'breadcrumbs'. The attribute can be a
string or a method. If it is a method it needs to accept two arguments
(args and kwargs) which correspond to the arguments of the view.

Example: request.path == '/users/foo/config/'

Views:

def config(request, ...):
    ...
config.breadcrumbs=u'Config'

def user(request, username):
    ...
user.breadcrumbs=lambda args, kwargs: args[1]

def users(request):
    ...
users.breadcrumbs='Users'


The URL 
    /users/foo/config/
will get to these breadcrumbs:
    Users>>foo>>Config

All except the last breadcrumb will be links.

Implemented with Django's resolve(url)

Usage:
 breadcrumbs, default_title = breadcrumbs.get_breadcrumbs(request)
     breadcrumbs: SafeUnicode HTML String
     default_title: Unicode String with the name of the current view.

Let Hansel and Grethel find their way home:
  http://en.wikipedia.org/wiki/Hansel_and_Gretel

'''

def link_callback_default(url, bc):
    return mark_safe(u'<a href="%s">%s</a>' % (
        urlquote(url), escape(bc)))

def join_callback_default(breadcrumbs):
    return mark_safe(u'<div class="breadcrumbs">%s</div>' % (join('>>', breadcrumbs)))

def get_breadcrumbs(request, link_callback=None, join_callback=None):
    if link_callback is None:
        link_callback=link_callback_default
    if join_callback is None:
        join_callback=join_callback_default
    path_info=request.META['PATH_INFO']
    url=path_info
    breadcrumbs=[]
    resolver = urlresolvers.get_resolver(None)
    count=0
    while True:
        count+=1
        assert count<1000, count
        callback=None
        try:
            callback, callback_args, callback_kwargs = resolver.resolve(url)
        except http.Http404, exc:
            pass
        else:
            bc=getattr(callback, 'breadcrumbs', None)
            if not callback.__module__.startswith('django.'):
                assert bc!=None, u'Callback %s.%s function breadcrumbs does not exist.' % (
                    callback.__module__, callback.__name__)
                sub_crumbs=[]
                if isinstance(bc, basestring):
                    pass
                elif hasattr(bc, '__call__'):
                    bc=bc(callback_args, callback_kwargs)
                    if isinstance(bc, tuple):
                        # The callable can return a tuple. The first entry is
                        # the name, the second is a tuple list of (url, name)
                        # Example .../objects/123/ (Object 123 is part of Object 99):
                        # Objects>>99>>123
                        bc, sub_crumbs = bc
                else:
                    raise Exception('Unkown type for breadcrumbs attribute: %s %s %r' % (
                        type(bc), bc, bc))
                if url!=path_info:
                    bc=link_callback('%s%s' % (request.META['SCRIPT_NAME'], url), bc)
                breadcrumbs.append(bc)
                for bc_url, name in sub_crumbs:
                    breadcrumbs.append(link_callback(bc_url, name))
                
        # Parent URL heraussuchen.
        if url=='/':
            break
        url=urljoin(url, '..')
    assert breadcrumbs
    default_title=breadcrumbs[0]
    breadcrumbs.append('')
    breadcrumbs.reverse()
    joined=join_callback(breadcrumbs)
    return (joined, default_title)

#def test_all_views():
#    u'''
#    Unittest: Check if all you views have a breadcrumbs()
#    attribute.
#
#    Django views are ignored.
#    '''
#    resolver=urlresolvers.get_resolver(None)
#    missing=[]
#    for function, patterns in resolver.reverse_dict.items():
#        if not function:
#            continue
#        sub_resolver=patterns[0]
#        if isinstance(function, basestring): 
#            continue
#        if function.__module__.startswith('django.'):
#            continue
#        name='%s.%s' % (function.__module__, function.__name__)
#        if not hasattr(function, 'breadcrumbs'):
#            missing.append(name)
#            continue
#        bc=function.breadcrumbs
#        if isinstance(bc, basestring):
#            try:
#                unicode(bc)
#            except UnicodeError, exc:
#                missing.append('UnicodeError, %s: %s' % (name, exc))
#    missing.sort()
#    assert not missing, 'Missing breadcrumbs function: %s' % (missing)
