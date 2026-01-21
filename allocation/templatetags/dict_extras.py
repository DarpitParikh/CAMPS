from django import template

register = template.Library()

@register.filter
def get_item(value, key):
    """Safe dict lookup for templates."""
    try:
        return value.get(key)
    except Exception:
        return None
