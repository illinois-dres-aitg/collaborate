"""This file is for populating the database with projects,  users,  etc whenever
I empty it. Run as a standalone script!"""

from collab.project.models import CollabProject, ProjectMembership
from django.contrib.auth.models import User
from collab.profiles.models import UserProfile
import datetime
from random import choice, randrange

users = (
('WhiteAdmin', 'mueen@nawaz.org', 'White', 'Admin', True, False), 
('WhiteUser', 'mueen@nawaz.org', 'White', 'User', True, False), 
('johndoe', 'mueen@nawaz.org', 'John', 'Doe', True, False), 
('jongund', 'jongund@uiuc.edu', 'Jon', 'Gunderson', True, False), 
('hadi', 'hadi@uiuc.edu', 'Hadi', 'Rangin', True, False), 
('someone', 'mueen@nawaz.org', 'Some', 'One', True, False), 
('noone', 'mueen@nawaz.org', 'No', 'One', True, False), 
('mueen', 'mueen@nawaz.org', 'Mueen', 'Nawaz', True, False), 
)


def create_users(users):
    
    for person in users:
        user = User(username=person[0], email=person[1], first_name=person[2], last_name=person[3], is_active=person[4], is_superuser=person[5])
        user.set_password(person[0])
        user.save()


def create_projects():
    Now = datetime.datetime.now()
    whiteboard = CollabProject(name='WhiteBoard', slug='WhiteBoard', start_date=Now)
    whiteboard.save()
    redboard = CollabProject(name='RedBoard', slug='RedBoard', start_date=Now)
    redboard.save()
    
def create_members(users):
    whiteboard = CollabProject.objects.get(slug='WhiteBoard')
    redboard = CollabProject.objects.get(slug='RedBoard')
    states = [True, False]
    
    for person in users:
        user = User.objects.get(username=person[0])
        if user.username=='WhiteAdmin':
            p = ProjectMembership(person=user, project=whiteboard, is_admin=True)
            p.save()
            if choice(states):
                p = ProjectMembership(person=user, project=redboard, is_admin=True)
                p.save()
            continue
        if user.username=='WhiteUser':
            p = ProjectMembership(person=user, project=whiteboard)
            p.save()
            if choice(states):
                p = ProjectMembership(person=user, project=redboard, is_admin=False)
                p.save()
            continue
        if user.username=='jongund':
            p = ProjectMembership(person=user, project=whiteboard, is_admin=True)
            p.save()
            n = ProjectMembership(person=user, project=redboard)
            n.save()
            continue
        if user.username=='hadi':
            p = ProjectMembership(person=user, project=whiteboard)
            p.save()
            n = ProjectMembership(person=user, project=redboard, is_admin=True)
            n.save()
            continue
        if choice(states):
            p = ProjectMembership(person=user, project=whiteboard)
            p.save()
        else:
            p = ProjectMembership(person=user, project=redboard)
            p.save()
            continue
        if choice(states):
            p = ProjectMembership(person=user, project=redboard)
            p.save()
    
    


def create_profiles():
    
    affiliations = ['Small University', 'UIUC', 'Big University']
    
    users = User.objects.all()
    for user in users:
        userprofile = UserProfile(user=user, affiliation=choice(affiliations))
        userprofile.save()
    

create_users(users)
create_profiles()
create_projects()
create_members(users)

