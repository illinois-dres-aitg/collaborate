from django.db import models
from django.contrib.auth.models import User
from django.db.models import get_models as django_get_models
from django.db.models import permalink

def get_security_models():
    """Returns a list of the names of all models that will be controlled by the privilege system"""
    return [model._meta.verbose_name for model in django_get_models() if model.__dict__.get('SECURITY',  False)]

class CollabProject(models.Model):

    def save(self, *args, **kwargs):
        """Create the required privileges for the new project"""
        
        if not self.pk:
            # I need to run super first because then privilege won't save a few lines below - 
            # as it has no project to tie to.
            super(CollabProject,  self).save(*args, **kwargs)
            
            # Create an AnonymousRole:
            AnonymousRole = Role(name='AnonymousRole', project=self)
            AnonymousRole.save()

	    # Need to save it here so that it can get a primary key -
	    # needed later when we save/append the privilege to it.
            
            
            for model in ['documentation'] + get_security_models():
                for ptype in Privilege.TYPE_CHOICES:
                    privilege = Privilege(permission_type=ptype[0], related_model=model, project=self)
                    privilege.save()
                    if ptype[0]=='Viewable':
                        AnonymousRole.privileges.add(privilege)

            # Add announcements privilege
            for ptype in Privilege.TYPE_CHOICES:
                privilege = Privilege(permission_type=ptype[0], related_model='announcements', project=self)
                privilege.save()
                if ptype[0]=='Viewable':
                    AnonymousRole.privileges.add(privilege)
            
            AnonymousRole.save()
            
            self.default_role = AnonymousRole
            super(CollabProject, self).save(*args, **kwargs)
        else:
            super(CollabProject,  self).save(*args, **kwargs)

    SECURITY = True
    
    name = models.CharField("Project Name",  max_length=80, unique=True)
    slug = models.SlugField(unique=True, help_text=u'The slug is used in the URL for the group. Must be unique consist of letters, numbers or hyphens.')
    active = models.BooleanField(default=True)
    summary = models.TextField(null=True, blank=True, verbose_name="Overview")
    mailing_list_url = models.URLField(null=True, blank=True, verify_exists=False)
    documentation = models.TextField(null=True, blank=True)

    # Originally, it was intended to have a simple announcement field.
    # The announce_expire field came much later. Ideally, this should be
    # spun off as a model of its own.
    announcements = models.TextField(null=True, blank=True)
    announce_expire = models.DateField(null=True, blank=True, help_text='Date the announcement will expire. If left blank, the announcement will remain until removed.', verbose_name='Expiry Date')

    # Not sure if this is good! It will know what users are "associated" with it.
    users = models.ManyToManyField(User,  verbose_name="Members",  null=True,  blank=True,  related_name='projects', through='ProjectMembership')
    start_date = models.DateField("Date Created")
    subgroup = models.ForeignKey('self', null=True, blank=True, editable=False)
    
    default_role = models.OneToOneField('Role', related_name='default_for', null=True, blank=True)
    
    @permalink
    def get_absolute_url(self):
        return ('project_summary', [str(self.slug)])
    
    def __unicode__(self):
        return self.name
    
    # This function allows stuff like project.admin.all(), etc.
    @property
    def admin(self):
        return User.objects.filter(projects__id=self.id, projectmembership__is_admin=True)

    # This function returns a query with only active users. 
    @property
    def active_users(self):
        return User.objects.filter(projectmembership__projects__id=self.id, projectmembership__active=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'collaboration group'


class ProjectMembership(models.Model):
    """Takes care of the relationship between users and projects. In particular,
    it stores if a user is an admin or not."""
    
    person = models.ForeignKey(User)
    project = models.ForeignKey(CollabProject)
    is_admin = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        """Ensure that a user can't be in a project more than once!"""
        
        existing_memberships = ProjectMembership.objects.filter(person=self.person, project=self.project)
        if existing_memberships:
            # This sets the ID of self to the one already found - ensuring that no new 
            # member is created. 
            self.id = existing_memberships[0].id
        super(ProjectMembership, self).save(*args, **kwargs)

class Privilege(models.Model):
    """Class for handling privileges"""
    
    TYPE_CHOICES = (
                    ('Viewable',  'Viewable'), 
                    ('Editable',  'Editable'), 
                )
    permission_type = models.CharField(max_length=15,  choices=TYPE_CHOICES)
    related_model = models.CharField(max_length=40)
    project = models.ForeignKey(CollabProject,  related_name='privileges', db_index=True)
    
    def __unicode__(self):
        return self.related_model + ' ' + self.permission_type
    


class Role(models.Model):
    
    def delete(self,  *args,  **kwargs):
        """Want to ensure that the AnonymousRole will not be deleted"""
        
        if self.name == 'AnonymousRole':
            pass
        else:
            super(Role, self).delete(*args, **kwargs)
    
    name = models.CharField("Role Name", max_length=20)
    project = models.ForeignKey(CollabProject, related_name='roles', db_index=True)
    # I'm told the verbose_name in the line below is redundant - no harm done in leaving it there.
    users = models.ManyToManyField(User, verbose_name="Users", null=True, blank=True, related_name='roles')
    privileges = models.ManyToManyField(Privilege, null=True, blank=True, related_name='roles')

    def __unicode__(self):
        return self.name
    
    
    class Meta:
        unique_together = (("name", "project"))

    @models.permalink
    def get_absolute_url(self):
        return ('role_edit', [str(self.project.slug), str(self.id)])
