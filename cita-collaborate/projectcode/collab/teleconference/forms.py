from django import forms
from django.forms import extras 
from collab.project.models import CollabProject
from models import TeleConference, Minutes
from django.contrib.auth.models import User
import datetime
from collab.forms import UserMultipleChoiceField, ModelFormTextArea

HOUR_CHOICES = (
                ('0', '00'), 
                ('1', '01'), 
                ('2', '02'), 
                ('3', '03'), 
                ('4', '04'), 
                ('5', '05'), 
                ('6', '06'), 
                ('7', '07'), 
                ('8', '08'), 
                ('9', '09'), 
                ('10', '10'), 
                ('11', '11'), 
                ('12', '12'), 
                ('13', '13'), 
                ('14', '14'), 
                ('15', '15'), 
                ('16', '16'), 
                ('17', '17'), 
                ('18', '18'), 
                ('19', '19'), 
                ('20', '20'), 
                ('21', '21'), 
                ('22', '22'), 
                ('23', '23'), 
            )

MINUTES_CHOICES = (
                   ('0', '00'), 
                   ('15', '15'), 
                   ('30', '30'), 
                   ('45', '45'), 
                )

TZ_CHOICES = (
                ('Pacific', 'Pacific'), 
                ('Mountain', 'Mountain'), 
                ('Central', 'Central'), 
                ('Eastern', 'Eastern'), 
                ('UTC', 'UTC'), 
              )

class SelectDateTimeWidget(forms.MultiWidget):
    """
    A Widget that splits datetime input into one SelectDateWidget field (for the date) and an <input type="text"> box for the time.
    """
    def __init__(self, attrs=None):
        widgets = (forms.extras.SelectDateWidget(attrs=attrs), forms.TextInput(attrs=attrs))
        super(SelectDateTimeWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return [value.date(), value.time().replace(microsecond=0)]
        return [None, None]

class SelectTimeWidget(forms.MultiWidget):
    """
    A Widget that splits time input to two select fields: One for hour and one for minutes.
    The minutes are in increments of 15.
    """

    def __init__(self, attrs=None):
        widgets = (forms.Select(attrs=attrs, choices=HOUR_CHOICES), forms.Select(attrs=attrs, choices=MINUTES_CHOICES), forms.Select(attrs=attrs, choices=TZ_CHOICES))
        super(SelectTimeWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            lst = map(unicode, [value.hour, value.minute, value.tzinfo])
            if lst[2] == u'None':
                lst[2] = 'Central'
            return lst
        return [None, None]

class SelectDurationWidget(forms.MultiWidget):
    """
    A Widget that splits time input to two select fields: One for hour and one for minutes.
    The minutes are in increments of 15.
    
    Same as above, but without the time zone. 
    
    Hackish way to do this, but subclassing would be pointless here.
    """

    def __init__(self, attrs=None):
        widgets = (forms.Select(attrs=attrs, choices=HOUR_CHOICES), forms.Select(attrs=attrs, choices=MINUTES_CHOICES))
        super(SelectDurationWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            lst = map(unicode, [value.hour, value.minute])
            return lst
        return [None, None]


class SelectTimeField(forms.MultiValueField):
    """Custom field for handling the time input."""
    
    def __init__(self, fields=(), *args, **kwargs):
        fields = (forms.ChoiceField(choices=HOUR_CHOICES), forms.ChoiceField(choices=MINUTES_CHOICES), forms.ChoiceField(choices=TZ_CHOICES))
        super(SelectTimeField, self).__init__(fields, *args, **kwargs)
    
    def compress(self, data_list):
        """Method for converting the two number strings to a time"""
        return [datetime.time(hour=int(data_list[0]), minute=int(data_list[1])), data_list[2]]

class SelectDurationField(forms.MultiValueField):
    """Custom field for handling the time input."""
    
    def __init__(self, fields=(), *args, **kwargs):
        fields = (forms.ChoiceField(choices=HOUR_CHOICES), forms.ChoiceField(choices=MINUTES_CHOICES))
        super(SelectDurationField, self).__init__(fields, *args, **kwargs)
    
    def compress(self, data_list):
        """Method for converting the two number strings to a time"""
        return "%s:%s" % (data_list[0], data_list[1]) 


class TeleConferenceForm(ModelFormTextArea):

    def __init__(self, project_id, *args, **kwargs):
        """
        Constructor for TeleConferenceForm - needed to limit the users to only that project.
        
        Note: That's what it was for originally. Then I moved participants to minutes - so I didn't need
        this initializer. But for some reason, things fail if I remove it and edit the corresponding view.
        Keeping it here for now as it doesn't really do any harm. 
        
        See bug 51.
        """
        super(TeleConferenceForm, self).__init__(*args, **kwargs)
        self.project_id = project_id
        self.fields["date"].initial=datetime.datetime.now()
    
#    date = forms.DateField(widget=forms.extras.SelectDateWidget, initial=datetime.datetime.now())
    date = forms.DateField(widget=forms.extras.SelectDateWidget)
    time = SelectTimeField(widget=SelectTimeWidget, initial=datetime.time(8, 0))
    duration = SelectDurationField(widget=SelectDurationWidget, initial=datetime.time(1, 0))

    class Meta:
        model = TeleConference
        exclude = ('project', 'time', 'duration', )
    

class MinutesForm(ModelFormTextArea):

    def __init__(self, tele_id, *args,  **kwargs):
        """
        Constructor for MinutesForm - needed to limit the users to only that project.
        """
        super(MinutesForm, self).__init__(*args,  **kwargs)
        project_id = TeleConference.objects.get(id=tele_id).project.id
	self.fields["participants"].widget = forms.CheckboxSelectMultiple()
        self.fields["participants"].queryset = User.objects.filter(projects__id__exact=project_id, projectmembership__active=True).order_by('last_name')
        self.fields["participants"].help_text = ''
        self.teleconference_id = tele_id
    
    participants = UserMultipleChoiceField(User, required=False)
    other_participants = forms.CharField(max_length=Minutes.max_length_participants, help_text='Separate names with a comma.', required=False)
    
    class Meta:
        model = Minutes
        exclude = ('teleconference', 'other_participants', )

