from django.db import models

class SiteInfo(models.Model):
    """Contains fields such as 'Announcements' and 'Overview' that
    will show up on the main page."""
    
    announcements = models.TextField(null=True, blank=True)
    overview = models.TextField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        """Ensure that only one instance of this model exists"""
        
        if self.pk:
            super(SiteInfo, self).save(*args, **kwargs)
        else:
            if SiteInfo.objects.all()[:1]:
                pass
            else:
                super(SiteInfo, self).save(*args, **kwargs)
            
    class Meta:
        verbose_name = 'Site Information'
        verbose_name_plural = 'Site Information'
