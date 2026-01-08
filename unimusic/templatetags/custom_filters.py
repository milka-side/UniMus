"""
Django custom filters for UniMus project.
"""

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def replace(value, arg):
    old, new = arg.split(',')
    return value.replace(old, new)
