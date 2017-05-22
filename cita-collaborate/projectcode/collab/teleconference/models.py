from django.db import models
from django.contrib.auth.models import User
from collab.project.models import CollabProject
from collab.timezoneinfo import construct_timezones

class TeleConference(models.Model):
    """Stores information regarding a teleconference"""
    
    SECURITY = True
    
    time = models.DateTimeField(db_index=True)
    duration = models.TimeField(blank=True, null=True)
    agenda = models.TextField()
    location = models.CharField("Physical Location",  blank=True,  null=True, max_length=100)
    phone = models.CharField("Phone number",  blank=True,  null=True,  max_length=20)
    phone_code = models.CharField("Phone password",  blank=True,  null=True,  max_length=20)
    online_uri = models.URLField("Online URL",  blank=True,  null=True,  verify_exists=False)
    online_userid = models.CharField("Online UserID", blank=True,  null=True,  max_length=30)
    online_password = models.CharField(blank=True,  null=True,  max_length=30)
    online_instructions = models.TextField(blank=True,  null=True)
    other_instructions = models.TextField(blank=True,  null=True)
    notes = models.TextField(blank=True,  null=True)
    project = models.ForeignKey(CollabProject,  related_name='teleconference', db_index=True)

    @models.permalink
    def get_absolute_url(self):
        return ('tele_details', [str(self.project.slug), str(self.id)])

    def __unicode__(self):
        return self.agenda[:100]
    
    class Meta:
        verbose_name = 'teleconference'
    
    def timezones(self):
        """Return  the required timezones"""
        return construct_timezones(self.time.year)
    
    def return_times(self):
        """Returns datetime objects having the times in all the timezones given
        by the timezones method"""
        
        tzs = construct_timezones(self.time.year)
        t = self.time.replace(tzinfo=tzs[2])
        return zip([tz.__str__() for tz in tzs], [t.astimezone(tz) for tz in tzs])


class Minutes(models.Model):
    """Stores the minutes for a teleconference"""
    
    SECURITY = True
    
    teleconference = models.OneToOneField(TeleConference,  related_name='minutes')
    participants = models.ManyToManyField(User, blank=True, null=True, related_name='teleconferences')
    minutes_text = models.TextField()
    other_participants = models.CharField(blank=True, null=True, help_text='Separate names with a comma', max_length=1000)

    max_length_participants=1000

    def get_participants(self):
        """Function to return participants in alphabetic order by last name"""
        return self.participants.order_by('last_name')

    @models.permalink
    def get_absolute_url(self):
        return ('tele_details', [str(self.project.slug), str(self.teleconference.id)])

    def __unicode__(self):
        return self.minutes_text

    def project_name(self):
        return self.teleconference.project.slug
    project_name.short_description = 'Project'
    
    class Meta:
        verbose_name_plural = 'minutes'

