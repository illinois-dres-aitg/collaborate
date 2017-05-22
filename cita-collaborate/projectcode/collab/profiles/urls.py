"""
URLConf for Django user profile management.

Recommended usage is to use a call to ``include()`` in your project's
root URLConf to include this URLConf for any URL beginning with
'/profiles/'.

"""

from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse

import views
import views2


urlpatterns = patterns('',
#                       url(r'^changepassword/$', views2.pass_change, name='profiles_passchange'), 
                       url(r'^create/$',
                           views2.create_profile,
                           name='profiles_create_profile'),
                       url(r'^edit/$',
                           views2.edit_profile,
                           name='profiles_edit_profile'),
                       url(r'^(?P<username>\w+)/$',
                           views.profile_detail,
                           name='profiles_profile_detail'),
                       url(r'^(?P<username>\w+)/edit/$',
                           views2.edit_profile,
                           name='profiles_edit'),
                       url(r'^(?P<username>\w+)/contact/$',
                           views2.contact_user,
                           name='profiles_contact_user'),
#                       url(r'^$',
#                           views2.profile_list, 
#                           {'paginate_by': 20}, 
#                           name='profiles_profile_list'),
                       )
