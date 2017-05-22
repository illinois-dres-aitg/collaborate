from django import forms
from collab.forms import ModelFormTextArea
from models import UserProfile

class ProfileForm(ModelFormTextArea):
    """Form for filling out profiles"""
    
    def __init__(self, user, *args, **kwargs):
        """I need to bind this form to a user!"""
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.User = user
    
    def save(self, *args, **kwargs):
        """Need to save the data to the related User model"""
        self.User.first_name = self.cleaned_data['first_name']
        self.User.last_name = self.cleaned_data['last_name']
        self.User.email = self.cleaned_data['email']
        self.User.save()
        self.cleaned_data['user'] = self.User
        del self.cleaned_data['email']
        del self.cleaned_data['first_name']
        del self.cleaned_data['last_name']
        del self.User
        return super(ProfileForm, self).save(*args, **kwargs)

    # Note that the User model does not require the first and last names.
    # I'm enforcing it at the form level, though. 
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = UserProfile
        exclude = ('user', )

class PasswordReset(forms.Form):
    """When I coded this, I didn't realize Django had its own mechanism."""
    oldpassword = forms.CharField(widget=forms.PasswordInput())
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(PasswordReset, self).__init__(*args, **kwargs)

    def clean_oldpassword(self):
        if self.cleaned_data.get('oldpassword') and not self.user.check_password(self.cleaned_data['oldpassword']):
            raise forms.ValidationError('Please type your current password.')
        return self.cleaned_data['oldpassword']

    def clean_password2(self):
        if self.cleaned_data.get('password1') and self.cleaned_data.get('password2') and self.cleaned_data['password1'] != self.cleaned_data['password2']:
            raise forms.ValidationError('The new passwords are not the same')
        return self.cleaned_data['password2']

class ContactUserForm(forms.Form):
    """Contact form for one user to contact another"""
    
    email_message = forms.CharField(widget=forms.Textarea(attrs={'cols':72}), required=True, max_length=1024*10)



