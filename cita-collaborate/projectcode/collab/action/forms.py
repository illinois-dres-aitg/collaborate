from django import forms
from models import ActionItem
from django.forms import extras 
from django.contrib.auth.models import User
from collab.forms import UserMultipleChoiceField, UserChoiceField, ModelFormTextArea
import datetime
from django.contrib.formtools.preview import FormPreview


class ActionItemForm(ModelFormTextArea):
    """ModelForm for editing and adding action items"""

    def __init__(self, project_id, *args, **kwargs):
        """
        Constructor for ModelForm - needed to limit the users to only that project.
        """
        super(ActionItemForm, self).__init__(*args,  **kwargs)
        self.fields["owner"].queryset = User.objects.filter(projects__id=project_id, projectmembership__active=True).order_by('last_name')
        self.fields["owner"].help_text = ''
        self.project_id = project_id

    deadline = forms.DateField(widget=forms.extras.SelectDateWidget, initial=datetime.datetime.now())
    owner = UserChoiceField(User, label="Assigned To")
    
    class Meta:
        model = ActionItem
        exclude = ('project', 'last_updated', 'date_assigned', )



