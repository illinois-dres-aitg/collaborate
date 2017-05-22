"""This file was originally for fixing some changes made to the privilege
system, but is now just a generic script used to make changes to the DB
when the DB schema changes."""

from collab.project.models import Privilege, CollabProject, Role
from collab.helpers import cluster_by

def to_lower(privileges):
    """Convert all model names to lower case"""
    
    for p in privileges:
        p.related_model = p.related_model.lower()
        p.save()

def add_announcements(privileges):
    """Create an announcements privilege for all
    projects that don't have one. Add it to all roles."""
    
    organizedp = cluster_by(lambda x: x.project.slug, privileges)
    
    for plist in organizedp:
        if 'announcements' not in [p.related_model.lower() for p in plist]:
            project = plist[0].project
            print project.slug
            roles = project.roles.all()
            for ptype in Privilege.TYPE_CHOICES:
                newp = Privilege(permission_type=ptype[0], related_model='announcements', project=project)
                newp.save()
                if ptype[0] == 'Viewable':
                    for role in roles:
                        role.privileges.add(newp)

def change_privileges(privileges):
    for p in privileges:
        if p.related_model=='issueset':
            p.related_model = 'issue list'
            p.save()
            continue
        if p.related_model=='actionitem':
            p.related_model = 'action item'
            p.save()
            continue
        if p.related_model=='collabproject':
            p.related_model = 'collaboration group'
            p.save()
            continue

def add_documentation(privileges):
    """Create a documentation privilege for all
    projects that don't have one. Add it to all roles."""
    
    organizedp = cluster_by(lambda x: x.project.slug, privileges)
    
    for plist in organizedp:
        if 'documentation' not in [p.related_model.lower() for p in plist]:
            project = plist[0].project
            print project.slug
            roles = project.roles.all()
            for ptype in Privilege.TYPE_CHOICES:
                newp = Privilege(permission_type=ptype[0], related_model='documentation', project=project)
                newp.save()
                if ptype[0] == 'Viewable':
                    for role in roles:
                        role.privileges.add(newp)



def add_default_role():
    """Add a default role to all existing groups."""
    projects = CollabProject.objects.all()
    for project in projects:
        if not project.default_role:
            role = Role.objects.get(name="AnonymousRole", project=project)
            project.default_role = role
            project.save()
            print project.name
    
def remove_collab_priv():
    """Remove the collaboration group viewable privilege."""
    privileges = Privilege.objects.filter(related_model=CollabProject._meta.verbose_name).all()
    for privilege in privileges:
        print privilege.project.name
        privilege.delete()

def do_all():
#    privileges = Privilege.objects.all()
#    add_documentation(privileges)
#    add_default_role()
    remove_collab_priv()

do_all()
    
