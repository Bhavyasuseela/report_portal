from django import template
from reports.views import encrypt_filename

register = template.Library()

@register.filter
def encrypted_token(file_field):
    """
    Usage: {{ report.paper_doc|encrypted_token }}
    Returns a URL-safe encrypted token for the file's relative path.
    """
    if not file_field:
        return ''
    return encrypt_filename(file_field.name)

@register.simple_tag
def encrypted_file_url(file_field):
    """
    Usage: {% encrypted_file_url report.paper_doc %}
    Returns /file/?t=TOKEN — using a query param avoids browser
    re-encoding of base64 padding characters in URL path segments.
    """
    from django.urls import reverse
    if not file_field:
        return '#'
    token = encrypt_filename(file_field.name)
    # Use query param so = signs are not mangled by the browser
    return reverse('serve_encrypted_pdf') + '?t=' + token

@register.filter
def get_item(dictionary, key):
    """Usage: {{ my_dict|get_item:key }} — returns dictionary[key] or empty string."""
    return dictionary.get(key, '')
