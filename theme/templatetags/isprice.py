from django import template
from django.template import defaultfilters

register = template.Library()


# all prices are stored in pence, so register a filter to convert to pounds and show 2 decimal places
@register.filter(name="isprice")
def isprice(value, arg=2):
    return defaultfilters.floatformat(value / 100, arg)
