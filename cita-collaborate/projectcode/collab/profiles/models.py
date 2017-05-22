"""
A model for storing profile information for the user.
"""

from django.db import models
from django.contrib.auth.models import User

TZ_CHOICES = (
                ('Pacific', 'Pacific'), 
                ('Mountain', 'Mountain'), 
                ('Central', 'Central'), 
                ('Eastern', 'Eastern'), 
                ('UTC', 'UTC'), 
              )


class UserProfile(models.Model):
    """This model stores a profile for each user that he/she can edit"""

    # Tie this model to a user. 
    user = models.ForeignKey(User, related_name='profile')
    affiliation = models.CharField(max_length=100)
    phone = models.CharField("Phone Number", null=True,  blank=True, max_length=30)
    job_title = models.CharField(max_length=80, null=True, blank=True)
    disability = models.TextField(null=True, blank=True, help_text='Only the group administrator will be able to view this')
    time_zone = models.CharField(max_length=20, null=True, blank=True, choices=TZ_CHOICES, help_text='Leave blank if you want to see all time zones every time a date is displayed')
    
    def get_absolute_url(self):
        return ('profiles_profile_detail', (), { 'username': self.user.username })
    get_absolute_url = models.permalink(get_absolute_url)
    
    def __unicode__(self):
        return  self.user.first_name + " " + self.user.last_name + ", " + self.affiliation
    
    
    class Meta:
        ordering = ['user__username', 'user__last_name']
