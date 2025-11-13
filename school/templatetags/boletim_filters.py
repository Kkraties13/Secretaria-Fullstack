from django import template

def dict_get(d, key):
    if isinstance(d, dict):
        return d.get(key)
    return d

register = template.Library()
register.filter('dict_get', dict_get)
