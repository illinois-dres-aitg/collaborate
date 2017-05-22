from django.http import HttpResponsePermanentRedirect

def redirect(request, path):
    """Redirect 'projects' to 'group' in URL"""

    return HttpResponsePermanentRedirect('/group/'+path)

redirect.breadcrumbs = ""
