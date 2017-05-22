from django import forms
from models import Role, CollabProject, Privilege
from django.contrib.auth.models import User
from collab.forms import UserMultipleChoiceField, SelectDateWidget, ModelFormTextArea


class RoleForm(ModelFormTextArea):

    def __init__(self, project_id,  *args,  **kwargs):
        """Constructor for RoleForm - needed to limit the users and privileges to only that project."""
        self.Clean = kwargs.get('clean',  True)
        # Remove it from keywords - seems to confuse the constructor in the next line.
        kwargs.pop('clean',  '')
        super(RoleForm, self).__init__(*args,  **kwargs)
        # project__id__exact is redundant. I can just do project__id if the var name matches exactly.
        self.fields["privileges"].widget = forms.CheckboxSelectMultiple()
        self.fields["privileges"].queryset = Privilege.objects.filter(project__id=project_id)
        self.fields["privileges"].help_text = ''
        self.fields["users"].widget = forms.CheckboxSelectMultiple()
        self.fields["users"].queryset = User.objects.filter(projects__id__exact=project_id).order_by('last_name')
        self.fields["users"].help_text = ''
        self.project_id = project_id
        
        if kwargs['instance']:
            self.name = kwargs['instance'].name
            project = CollabProject.objects.get(id=project_id)
            if project.default_role.name == kwargs['instance'].name:
                self.fields["make_default"].initial = True
        else:
            self.name = None
    
    users = UserMultipleChoiceField(User, required=False)
    make_default = forms.BooleanField(label="Make this the default role new users are added to", required=False)
    
    class Meta:
        model = Role
        # The project is fixed in the add_role view.
        exclude = ('project', )
    
    def clean_name(self):
        # Check if role already exists in that project. I need this even though I did a unique_together in the model.
        
        if self.name:
            # We don't have to check for conflicts with AnonymousRole, because
            # the user can't create it!
            if self.name == 'AnonymousRole':
                self.cleaned_data['name'] = 'AnonymousRole'
                return self.cleaned_data['name']
            elif self.name != self.cleaned_data['name']:
                self.Clean = True
            else:
                # User didn't modify the name - so he's not adding a new role.
                return self.cleaned_data['name']

        if self.Clean:
            if Role.objects.filter(project__id__exact=self.project_id).filter(name__exact=self.cleaned_data['name']).count():
                raise forms.ValidationError("Role " + self.cleaned_data['name'] + " already exists!")
            return self.cleaned_data['name']
        else:
            return self.cleaned_data['name']



class RoleBulkForm(forms.Form):
    """Form for bulk adding/removing people from/to different roles"""
    
    def __init__(self, project_id, *args, **kwargs):
        """Constructor:  needed to limit the users and roles to those of the given project."""
        super(RoleBulkForm, self).__init__(*args,  **kwargs)
        self.fields["users"].widget=forms.CheckboxSelectMultiple()
        self.fields["roles"].widget=forms.CheckboxSelectMultiple()
        self.fields["users"].queryset=User.objects.filter(projects__id__exact=project_id).order_by('last_name')
        self.fields["roles"].queryset=Role.objects.filter(project__id__exact=project_id)
    
    users = UserMultipleChoiceField(User)
    roles =  forms.ModelMultipleChoiceField(Role)

class MembersBulkForm(forms.Form):
    """Form for bulk adding/removing people from/to projects"""
    
    def __init__(self, project_id, task, project_limit_slug, *args, **kwargs):
        """Constructor:  needed to limit the users and roles to those of the given project."""
        super(MembersBulkForm, self).__init__(*args,  **kwargs)
        self.fields["users"].widget=forms.CheckboxSelectMultiple()
        if task=='add':
            if project_limit_slug:
                project_limit = CollabProject.objects.get(slug=project_limit_slug)
                self.fields["users"].queryset=User.objects.filter(projects__id__exact=project_limit.id).exclude(projects__id__exact=project_id).order_by('last_name')
            else:
                self.fields["users"].queryset=User.objects.filter(profile__isnull=False).exclude(projects__id__exact=project_id).order_by('last_name')
        elif task=='remove':
            self.fields["users"].queryset=User.objects.filter(projects__id__exact=project_id).order_by('last_name')
  
    users = UserMultipleChoiceField(User)

class ProjectInfoForm(ModelFormTextArea):
    """Form for adding summary info, announcements, etc. to the group"""
    
    class Meta:
        model = CollabProject
        fields = ('summary', 'mailing_list_url', 'name', 'slug', )
    
class ProjectInfoAdminsForm(ProjectInfoForm):
    """Same as the parent class, but allows one to modify admins
    as well. Used only if the requester(sp?) is the superuser."""

    def __init__(self, *args, **kwargs):
        """If user is the superuser, then also allow option to set the admins"""
        super(ProjectInfoForm, self).__init__(*args, **kwargs)
        self.fields["admins_to_add"].widget = forms.CheckboxSelectMultiple()
        self.fields["admins_to_add"].queryset = User.objects.filter(projects__id=self.instance.id, projectmembership__is_admin=False).order_by('last_name')
        self.fields["admins_to_add"].help_text = 'Make these members admins:'
        self.fields["admins_to_remove"].widget = forms.CheckboxSelectMultiple()
        self.fields["admins_to_remove"].queryset = self.instance.admin
        self.fields["admins_to_remove"].help_text = 'Revoke admin privileges for these members:'

        # If there are no admins to remove/add, just don't show that field!
        if not self.fields["admins_to_remove"].queryset.count():
            del self.fields["admins_to_remove"]
        if not self.fields["admins_to_add"].queryset.count():
            del self.fields["admins_to_add"]

    admins_to_add = UserMultipleChoiceField(User, required=False, label='Add as Admins')
    admins_to_remove = UserMultipleChoiceField(User, required=False, label='Remove Admins')
    
    
class MembersActiveForm(forms.Form):
    """Form for bulk activating/inactivating people in a project"""
    
    def __init__(self, project_id, task, *args, **kwargs):
        """Constructor:  needed to limit the users and roles to those of the given project."""
        super(MembersActiveForm, self).__init__(*args,  **kwargs)
        self.fields["users"].widget=forms.CheckboxSelectMultiple()
        if task=='activate':
            self.fields["users"].queryset=User.objects.filter(projects__id__exact=project_id, projectmembership__active=False).order_by('last_name')
        elif task=='inactivate':
            self.fields["users"].queryset=User.objects.filter(projects__id__exact=project_id, projectmembership__active=True).order_by('last_name')
  
    users = UserMultipleChoiceField(User)

class BulkSubscriptionForm(forms.Form):
    """Form to allow a user to request to join multiple groups, or 
    to leave them."""
    
    def __init__(self, groups, *args, **kwargs):
        """Limit potential projects to the ones provided."""
        super(BulkSubscriptionForm, self).__init__(*args, **kwargs)
        self.fields["projects"].widget=forms.CheckboxSelectMultiple()
        self.fields["projects"].queryset=groups        
        
    
    projects = forms.ModelMultipleChoiceField(CollabProject, required=False)

class CreateProjectForm(ModelFormTextArea):
    """Form for creating a new project"""
    
    def __init__(self, *args, **kwargs):
        super(CreateProjectForm, self).__init__(*args, **kwargs)
        
        self.fields["admins"].widget = forms.CheckboxSelectMultiple()
        self.fields["admins"].queryset = User.objects.filter(is_active=True, profile__isnull=False)
        self.fields["admins"].help_text = ''

    admins = UserMultipleChoiceField(User)

    class Meta:
        model = CollabProject
        exclude = ('subgroup', 'start_date', 'users', 'default_role', )

class DocumentationForm(ModelFormTextArea):
    """Form for editing documentation"""
    
    class Meta:
        model = CollabProject
        fields = ('documentation', )

class AnnouncementForm(ModelFormTextArea):
    """Form for editing announcements"""
    
    def __init__(self, *args, **kwargs):
        """Set the proper widget for the expiry date"""
        
        super(AnnouncementForm, self).__init__(*args, **kwargs)
        self.fields["announce_expire"].widget = SelectDateWidget()
    
    class Meta:
        model = CollabProject
        fields = ('announcements', 'announce_expire', )
