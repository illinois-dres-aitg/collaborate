from django.conf.urls.defaults import *
from django.contrib import admin
from django.views.generic import list_detail
from collab import project,  teleconference,  action
import project.views
import teleconference.views 
import action.views
import issues.views
import datetime
import siteinfo.views
import views
from collab.feeds import NextTeleconferences

admin.autodiscover()

feeds = {
        'teleconferences': NextTeleconferences, 
    }

# Some day I need to break these up into separate files (one for
# teleconferences, one for issues, etc).


urlpatterns = patterns('',
    # This one is for handling accounts (registration, password change, etc)
    (r'^accounts/', include('collab.registration.urls')),
    # This one is for handling user profiles.
    (r'^profiles/', include('collab.profiles.urls')),
    # Admin
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/(.*)', admin.site.root),

    # Comments
    (r'^comments/', include('django.contrib.comments.urls')),

    # Feeds
    (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}), 
    
    # Projects (i.e. "Groups")
    url(r'^$',  project.views.all_projects, name='projects'),
    url(r'^edit_site_info/$', siteinfo.views.change_siteinfo, name='edit_site_info'), 
    url(r'^create_project/$', project.views.create_project, name='create_project'), 
    url(r'^teleconferences/$', teleconference.views.global_teleconferences, name='global_teleconferences'),
    url(r'^about/$', project.views.about, name='about'),
    url(r'^groups?/$', project.views.all_projects), 
    url(r'^(?P<join_or_leave>(join|leave))groups/$',  project.views.join_leave_projects,  name='join_leave_projects'), 
    url(r'^group/([\w-]+)/$',  project.views.project_info,  name='project_summary'),  
    url(r'^group/(?P<project_name>[\w-]+)/members/$', project.views.member_list, name='project_members'), 
    url(r'^group/(?P<project_name>[\w-]+)/members/download/$', project.views.members_download, name='project_members_download'), 
    url(r'^group/(?P<project_name>[\w-]+)/members/(?P<all>all)/$', project.views.member_list, name='project_members_all'), 
    url(r'^group/(?P<project_name>[\w-]+)/members/filter/$', project.views.members_add_filter, name='project_members_filter'), 
    url(r'^group/(?P<project_name>[\w-]+)/members/(?P<add_or_remove>add)/$',  project.views.members_bulk_add_remove, name='members_add'), 
    url(r'^group/(?P<project_name>[\w-]+)/members/(?P<add_or_remove>add)/project_limit/(?P<project_limit>[\w-]*)/$',  project.views.members_bulk_add_remove, name='members_add_filter'), 
    url(r'^group/(?P<project_name>[\w-]+)/members/(?P<add_or_remove>remove)/$',  project.views.members_bulk_add_remove, name='members_remove'), 
    url(r'^group/(?P<project_name>[\w-]+)/addrole/$',  project.views.add_edit_role, name='role_add'), 
    url(r'^group/(?P<project_name>[\w-]+)/roles/$',  project.views.roles_overview, name='roles_overview'), 
    url(r'^group/(?P<project_name>[\w-]+)/roles/(?P<add_or_remove>(addtoroles?|removefromroles?))/$',  project.views.role_bulk_add_remove, name='role_add_remove'), 
    url(r'^group/(?P<project_name>[\w-]+)/roles/(?P<role_id>\d+)/edit/$',  project.views.add_edit_role, name='role_edit'), 
    url(r'^group/(?P<project_name>[\w-]+)/roles/(?P<role_id>\d+)/edit/delete/$',  project.views.delete_role, name='role_delete'), 
    url(r'^group/(?P<project_name>[\w-]+)/members/add/(?P<userid>[\w-]+)/$',  project.views.add_user, name='add_single_user'), 
    url(r'^group/(?P<project_name>[\w-]+)/members/(?P<activate_or_inactivate>(inactivate|activate))/$',  project.views.inactivate, name='project_members_activate'), 
    url(r'^group/(?P<project_name>[\w-]+)/subscribe/$',  project.views.subscribe, name='project_subscribe'), 
    url(r'^group/(?P<project_name>[\w-]+)/editinfo/$',  project.views.edit_info, name='project_edit'), 
    
    # Teleconferences
    url(r'^group/(?P<project_name>[\w-]+)/teleconferences/$',  teleconference.views.all_teleconferences, name='tele_overview'), 
    url(r'^group/(?P<project_name>[\w-]+)/addtele/$',  teleconference.views.add_edit_tele, name='tele_add'), 
    url(r'^group/(?P<project_name>[\w-]+)/teleconferences/(?P<tele_id>\d+)/$',  teleconference.views.details, name='tele_details'), 
    url(r'^group/(?P<project_name>[\w-]+)/teleconferences/(?P<tele_id>\d+)/edit/$',  teleconference.views.add_edit_tele, name='tele_edit'), 
    url(r'^group/(?P<project_name>[\w-]+)/teleconferences/(?P<tele_id>\d+)/delete/$',  teleconference.views.delete_tele, name='tele_delete'), 
    url(r'^group/(?P<project_name>[\w-]+)/teleconferences/(?P<tele_id>\d+)/editminutes/$',  teleconference.views.add_edit_minutes, name='minutes_edit'), 
    
    # Action items
    url(r'^group/(?P<project_name>[\w-]+)/addaction/$', action.views.add_edit_action, name='action_add'), 
    url(r'^group/(?P<project_name>[\w-]+)/action/(?P<action_id>\d+)/$', action.views.details,  name='action_details'), 
    url(r'^group/(?P<project_name>[\w-]+)/action/(?P<action_id>\d+)/edit/$', action.views.add_edit_action, name='action_edit'), 
    url(r'^group/(?P<project_name>[\w-]+)/action/(?P<action_id>\d+)/delete/$', action.views.delete_action, name='action_delete'), 
    url(r'^group/(?P<project_name>[\w-]+)/action/$', action.views.action_overview, name='action_overview'), 
    
    # Issues and issue sets
    url(r'^group/(?P<project_name>[\w-]+)/addissueset/$', issues.views.add_edit_issueset, name='issueset_add'), 
    url(r'^group/(?P<project_name>[\w-]+)/issuesets/(?P<issueset_id>\d+)/edit/$', issues.views.add_edit_issueset, name='issueset_edit'), 
    url(r'^group/(?P<project_name>[\w-]+)/issuesets/$', issues.views.issuesets_overview, name='issuesets_overview'), 
    url(r'^group/(?P<project_name>[\w-]+)/issuesets/(?P<issueset_id>\d+)/$', issues.views.details_issueset,  name='issueset_details'), 
    url(r'^group/(?P<project_name>[\w-]+)/issuesets/(?P<issueset_id>\d+)/delete/$', issues.views.delete_issueset, name='issueset_delete'), 
    url(r'^group/(?P<project_name>[\w-]+)/issuesets/(?P<issueset_id>\d+)/addissue/$', issues.views.add_edit_issue, name='issue_add'), 
    url(r'^group/(?P<project_name>[\w-]+)/issuesets/(?P<issueset_id>\d+)/issues/(?P<issue_id>\d+)/edit/$', issues.views.add_edit_issue, name='issue_edit'), 
    url(r'^group/(?P<project_name>[\w-]+)/issuesets/(?P<issueset_id>\d+)/issues/(?P<issue_id>\d+)/$', issues.views.details_issue,  name='issue_details'), 
    url(r'^group/(?P<project_name>[\w-]+)/issuesets/(?P<issueset_id>\d+)/issues/(?P<issue_id>\d+)/delete/$', issues.views.delete_issue, name='issue_delete'), 
    url(r'^group/(?P<project_name>[\w-]+)/issuesets/(?P<issueset_id>\d+)/latest/$', issues.views.details_issueset_flat,  name='issueset_latest'), 
    url(r'^group/(?P<project_name>[\w-]+)/issuesets/latest/$', issues.views.issues_flat, name='issues_latest'),
    url(r'^group/(?P<project_name>[\w-]+)/issuesets/(?P<issueset_id>\d+)/issues/(?P<issue_id>\d+)/upload/$', issues.views.upload_image, name='image_upload'),
    url(r'^image/(?P<image_id>\d+)/delete/$', issues.views.delete_issue, name='image_delete'),
    
    # Documentation
    url(r'^group/(?P<project_name>[\w-]+)/documentation/$', project.views.documentation, name='documentation'),
    url(r'^group/(?P<project_name>[\w-]+)/documentation/edit/$', project.views.edit_doc, name='doc_edit'), 
    
    # Announcements
    url(r'^group/(?P<project_name>[\w-]+)/announcements/edit/$', project.views.edit_announcement, name='announce_edit'), 

    # Redirecting "projects" to "group"                   
    url(r'^projects/(.*)', views.redirect), 
   
)
