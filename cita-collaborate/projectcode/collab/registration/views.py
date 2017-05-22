"""
Views which allow users to create and activate accounts.

"""


from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string

from collab.registration.forms import RegistrationForm, ResendKeyForm
from collab.registration.models import RegistrationProfile
from collab.helpers import handle_privilege


def activate(request, activation_key, template_name='registration/activate.html'):
    """
    Activates a ``User``'s account, if their key is valid and hasn't
    expired.
    
    By default, uses the template ``registration/activate.html``; to
    change this, pass the name of a template as the keyword argument
    ``template_name``.
    
    **Context:**
    
    account
        The ``User`` object corresponding to the account, if the
        activation was successful. ``False`` if the activation was not
        successful.
    
    expiration_days
        The number of days for which activation keys stay valid after
        registration.
    
    **Template:**
    
    registration/activate.html or ``template_name`` keyword argument.
    
    """
    activation_key = activation_key.lower() # Normalize before trying anything with it.
    account = RegistrationProfile.objects.activate_user(activation_key)
    return render_to_response(template_name,
                              { 'account': account,
                                'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS },
                              context_instance=RequestContext(request))

activate.breadcrumbs = 'Account activation'


def register(request, success_url='/accounts/register/complete/',
             form_class=RegistrationForm, profile_callback=None,
             template_name='registration/registration_form.html'):
    """
    Allows a new user to register an account.
    
    Following successful registration, redirects to either
    ``/accounts/register/complete/`` or, if supplied, the URL
    specified in the keyword argument ``success_url``.
    
    By default, ``registration.forms.RegistrationForm`` will be used
    as the registration form; to change this, pass a different form
    class as the ``form_class`` keyword argument. The form class you
    specify must have a method ``save`` which will create and return
    the new ``User``, and that method must accept the keyword argument
    ``profile_callback`` (see below).
    
    To enable creation of a site-specific user profile object for the
    new user, pass a function which will create the profile object as
    the keyword argument ``profile_callback``. See
    ``RegistrationManager.create_inactive_user`` in the file
    ``models.py`` for details on how to write this function.
    
    By default, uses the template
    ``registration/registration_form.html``; to change this, pass the
    name of a template as the keyword argument ``template_name``.
    
    **Context:**
    
    form
        The registration form.
    
    **Template:**
    
    registration/registration_form.html or ``template_name`` keyword
    argument.
    
    """
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            new_user = form.save(profile_callback=profile_callback)
            return HttpResponseRedirect(success_url)
    else:
        form = form_class()
    return render_to_response(template_name,
                              { 'form': form },
                              context_instance=RequestContext(request))

register.breadcrumbs = 'Register'

def resend_key(request):
    """Display a form allowing user to request a new key.
    It checks to see if the user is already activated.
    It also checks to see if the user had been activated before, 
    in which case he/she is not allowed to re-activate (perhaps
    he's been "banned"."""
    
    if request.method == 'POST':
        form = ResendKeyForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return handle_privilege(request, "There is no user associated with that email address!", reverse('registration_register'))
            if user.is_active:
                return handle_privilege(request, message="The user associated with that email address has already been activated!", redirect_url=reverse('auth_login'))
            try:
                registration_profile = RegistrationProfile.objects.get(user=user)
            except RegistrationProfile.DoesNotExist:
                return handle_privilege(request, "That user cannot be activated.", '/')
            if "AlreadyActivated" in registration_profile.activation_key:
                return handle_privilege(request, "That user cannot be activated.", '/')
            
            # Everything's OK. Send the email.
            from django.core.mail import send_mail
            from django.contrib.sites.models import Site
            current_site = Site.objects.get_current()
            subject = render_to_string('registration/activation_email_subject.txt',
                                       { 'site': current_site })
            # Email subject *must not* contain newlines
            subject = ''.join(subject.splitlines())
            
            message = render_to_string('registration/activation_email.txt',
                                       { 'activation_key': registration_profile.activation_key,
                                         'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                                         'site': current_site })
            print message
            send_mail(subject, message, settings.REGISTRATION_FROM_EMAIL, [email])
            return handle_privilege(request, "A new activation email has been sent!", reverse('auth_login'))
    else:
        form = ResendKeyForm()
    return render_to_response('registration/request_key.html', { 'form': form }, context_instance=RequestContext(request))

resend_key.breadcrumbs = 'Resend activation key'
