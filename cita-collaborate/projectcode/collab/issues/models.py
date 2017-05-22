from django.db import models
from collab.project.models import CollabProject
from django.contrib.auth.models import User
from django.db.models import permalink
from django.core.signals import request_finished
from django.contrib.comments.signals import comment_was_posted
import datetime
from django.conf import settings

class IssueSet(models.Model):
    """Each issue is part of some issue set. A project can have multiple issue
    sets (e.g. one for each product of that project)."""
    
    SECURITY = True
    
    project = models.ForeignKey(CollabProject, related_name='issuesets', db_index=True)
    name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    
    def __unicode__(self):
        return self.name
    
    @permalink
    def get_absolute_url(self):
        return ('issueset_details', [str(self.project.slug), str(self.id)])
    
    class Meta:
        verbose_name = "issue list"


class Issue(models.Model):
    """Stores various accessibility issues people are having with a product"""
    
    SECURITY = True
    
    STATUS_CHOICES = (
                      ('Reported',  'Reported'), 
                      ('Data Collection',  'Data Collection'), 
                      ('Verification',  'Verification'), 
                      ('Fix in progress',  'Fix in progress'), 
                      ('Fixed', 'Fixed'), 
                    )
    
    PRIORITY_CHOICES = (
                        ('High', 'High'), 
                        ('Medium', 'Medium'), 
                        ('Low', 'Low'), 
                    )
    
    title = models.CharField(max_length=200)
    number = models.PositiveIntegerField(editable=False)
    status = models.CharField(max_length=30,  choices=STATUS_CHOICES, db_index=True)
    description = models.TextField()
    reporter = models.ForeignKey(User, verbose_name='Reported by')
    reported_date = models.DateTimeField("Issue reported date", auto_now_add=True, db_index=True)
    updated_date = models.DateTimeField("Issue updated date", auto_now=True, db_index=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, db_index=True)
    vendor_tracking = models.IntegerField(null=True,  blank=True)
    issueset = models.ForeignKey(IssueSet,  related_name='issues', db_index=True, verbose_name='Issue List')
    version = models.CharField("Product version", null=True, blank=True, max_length=30)
    module = models.CharField(max_length=30,  null=True, blank=True)
    section = models.CharField(max_length=30, null=True, blank=True)
    code = models.TextField("Code illustrating the issue", null=True, blank=True)
    snapshot = models.FileField(upload_to='images/%Y/%m/%d', null=True, blank=True)
    company_reported_date = models.DateField("Date the issue was reported to the company/entity", blank=True, null=True)
    company_response = models.TextField("Response from the company/entity", blank=True, null=True)
    estimated_fix = models.DateField("Estimated date of fix", blank=True, null=True)
    verified_fix = models.DateField("Date fix is verified", blank=True, null=True)
    fix_comment = models.TextField("Comment on fix", blank=True, null=True)

    class Meta:
        ordering = ['-number']
        unique_together = (('number', 'issueset'), )

    def save(self, *args, **kwargs):
        """
	Ensure that the issue number keeps incrementing per project -
        not overall. So if there is a group called WhiteBoard, and I
        create an issue in WhiteBoard, then it's first value is 1. If I
        then create an issue in RedBoard, its value will be 1, not 2.
	"""
        
        if not self.pk:
            try:
                issue = Issue.objects.filter(issueset=self.issueset).all()[0]
                self.number = issue.number + 1
            except IndexError:
                self.number = 1
        super(Issue, self).save(*args, **kwargs)
        

    def __unicode__(self):
        return self.title
    
    @permalink
    def get_absolute_url(self):
        return ('issue_details', [str(self.issueset.project.slug), str(self.issueset.id), str(self.id)])
    

def upload_path(instance, filename):
    """
    Function to determine location of uploaded image.
    """

    path = 'images/issues/' + str(instance.issue.id) + '/' + filename

    return path
    
	
class IssueImage(models.Model):
    """
    A model for an attached image to an issue.
    """

    img = models.ImageField(upload_to=upload_path, help_text="Maximum allowed size: "+str(settings.MAX_IMAGE_SIZE/1024)+" kilobytes.")
    desc = models.CharField(max_length=200)
    issue = models.ForeignKey(Issue, related_name='images')

    def size_in_kb(self):
	return self.img.size/1024

    def __unicode__(self):
	return self.desc


def comment_callback(sender, **kwargs):
    """
    Handler for a signal when a comment is saved. Essentially, it finds
    out which Issue the comment is attached to, and updates its
    updated_date field.
    """
    
    comment = kwargs['comment']
    if comment.content_type.model_class() == Issue:
        issue = Issue.objects.get(id=comment.object_pk)
        issue.updated_date = datetime.datetime.now()
        issue.save()

comment_was_posted.connect(comment_callback)
