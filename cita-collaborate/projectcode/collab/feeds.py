from django.contrib.syndication.feeds import Feed
from collab.teleconference.models import TeleConference
from collab.project.models import CollabProject
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
import datetime


class NextTeleconferences(Feed):
    """Feed for showing upcoming teleconferences.
    It can handle global,  or specific to a certain 
    collaboration group."""
    
    def get_object(self, bits):
        if len(bits) > 1:
            raise ObjectDoesNotExist
        if len(bits) == 0:
            return None
        return CollabProject.objects.get(slug=bits[0])
    
    def title(self, obj):
        if obj:
            return "iCITA Collaboration Groups: Upcoming Teleconferences for %s" % obj.name
        else:
            return "iCITA Collaboration Groups: Upcoming Teleconferences"
    
    def link(self, obj):
        print obj
        if obj:
            return reverse('tele_overview', kwargs={'project_name': obj.slug})
        else:
            return '/'
    
    def description(self, obj):
        return "Upcoming Teleconferences"
    
    def items(self, obj):
        if obj:
            return TeleConference.objects.filter(project=obj, time__gte=datetime.date.today(), time__lte=(datetime.date.today()+datetime.timedelta(days=7))).order_by('time').all()
        else:
            return TeleConference.objects.filter(time__gte=datetime.date.today(), time__lte=(datetime.date.today()+datetime.timedelta(days=7))).order_by('time').all()
