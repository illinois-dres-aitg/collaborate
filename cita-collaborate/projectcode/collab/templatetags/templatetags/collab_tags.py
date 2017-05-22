from django import template

register = template.Library()

def getlabel(dictionary, keyval):
    """A filter that takes in a string, and returns dictionary[key]"""
    
    try:
        return dictionary.get(keyval).label
    except (TypeError, NameError, AttributeError):
        return ''

register.filter('getlabel', getlabel)
