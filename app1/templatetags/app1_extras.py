from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Template filter to get a value from a dictionary using a key.
    """
    return dictionary.get(key, '')

@register.filter(name='add_class')
def add_class(field, css_class):
    """Adds a CSS class to a form field widget."""
    return field.as_widget(attrs={"class": css_class})