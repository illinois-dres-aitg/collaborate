from django import forms
from models import IssueSet, Issue, IssueImage
from django.contrib.auth.models import User
from collab.forms import SelectDateWidget, ModelFormTextArea
import datetime
from django.conf import settings


class IssueSetForm(ModelFormTextArea):
    """Form for issue sets"""
    
    class Meta:
        model = IssueSet
        exclude = ('project', )

class IssueForm(ModelFormTextArea):
    """Form for issues"""
    
    def __init__(self, *args, **kwargs):
        """
	Set the times on all date fields to have initial values of
        today. Also limit the issueset field to display only issue sets
        from this project.
	"""
        
        if "issueset" in kwargs:
            issueset = kwargs["issueset"]
            del kwargs["issueset"]

        super(IssueForm, self).__init__(*args, **kwargs)
        self.fields["estimated_fix"].widget = SelectDateWidget()
        self.fields["issueset"].queryset = issueset.project.issuesets.all()

    class Meta:
        model = Issue
        exclude = ('number', 'reported_date', 'updated_date', 'reporter', 'snapshot',)

class ImageForm(forms.ModelForm):
    """
    Form for uploading images.
    """

    def clean_img(self):
	if self.cleaned_data["img"].size > settings.MAX_IMAGE_SIZE:
	    max_size = settings.MAX_IMAGE_SIZE/1024.
	    raise forms.ValidationError("The file should not be greater than %.0f kilobytes!" % max_size)
	else:
	    return self.cleaned_data["img"]

    class Meta:
	model = IssueImage
	exclude = ('issue',)
