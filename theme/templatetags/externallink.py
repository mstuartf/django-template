from django import template

register = template.Library()


# make sure all external links are prefixed with https so the browser does not attempt to open them as relative links
@register.filter(name="externallink")
def externallink(value):
    if value.startswith("http"):
        return value
    return "https://{}".format(value)
