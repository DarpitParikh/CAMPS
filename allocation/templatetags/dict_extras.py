from django import template

register = template.Library()

@register.filter
def get_item(value, key):
    """Safe dict lookup for templates."""
    try:
        return value.get(key)
    except Exception:
        return None

@register.filter
def initials(value):
    """Return uppercase initials for a string."""
    if not value:
        return ""
    stop_words = {"and", "or", "the", "of", "for", "to", "a", "an", "in", "on", "with", "by", "from", "at", "as"}
    parts = [p for p in str(value).split() if p and p.lower() not in stop_words]
    if len(parts) == 1:
        return parts[0].upper()
    return "".join(p[0].upper() for p in parts)
