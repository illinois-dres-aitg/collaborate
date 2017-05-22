from django.db import models
from django.contrib.auth.models import User
from collab.project.models import CollabProject
from django.db.models import permalink

class ActionItem(models.Model):
    """Model for action items"""
    
    SECURITY = True

    STATUS_CHOICES = (
                      ('Open',  'Open'), 
                      ('Closed',  'Closed'), 
                      ('Canceled',  'Canceled'), 
                    )
    
    owner = models.ForeignKey(User, related_name='action_items', db_index=True, verbose_name='assigned to')
    status = models.CharField(max_length=20,  choices=STATUS_CHOICES, db_index=True)
    date_assigned = models.DateField(auto_now_add=True, db_index=True)
    action = models.CharField("Action item summary", max_length=120)
    notes = models.TextField("Additional notes",  blank=True, null=True)
    url_desc = models.URLField("URL for supporting information", blank=True,  null=True, verify_exists=False)
    url_complete = models.URLField("Completed URL",  blank=True,  null=True)
    deadline = models.DateField(db_index=True)
    last_updated = models.DateTimeField(auto_now=True)
    project = models.ForeignKey(CollabProject,  related_name='action_items', db_index=True)
    
    def __unicode__(self):
        return self.action
    
    @permalink
    def get_absolute_url(self):
        return ('action_details', [str(self.project.slug), str(self.id)])
    
    class Meta:
        ordering = ['deadline']
