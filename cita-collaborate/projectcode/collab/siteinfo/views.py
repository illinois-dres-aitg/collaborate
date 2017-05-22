from models import SiteInfo
from django.contrib.auth.decorators import login_required
from django.views.generic.create_update import update_object

@login_required
def change_siteinfo(request):
    """Function to allow the modification of main page site information
    (announcements,  etc). Only superusers can do this."""
    
    if not request.user.is_superuser:
        handle_privilege(request, "You do not have permissions to access this page!", '/')
    
    # If no siteinfo object exists, then create one!
    siteinfo_list = SiteInfo.objects.all()[:1]
    
    if not siteinfo_list:
        siteinfo = SiteInfo()
        siteinfo.save()
    else:
        siteinfo = siteinfo_list[0]
    
    return update_object(request, model=SiteInfo, object_id=siteinfo.pk, post_save_redirect='/', login_required=True, template_name='siteinfo/edit_siteinfo.html')
    
change_siteinfo.breadcrumbs = 'Modify site metadata'
