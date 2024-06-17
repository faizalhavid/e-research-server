from django import template
register = template.Library()
import re

@register.filter
def get_item(list, index):
    if index < len(list):
        return list[index]
    else:
        return None
    
@register.filter(name='get_tuple_item')
def get_tuple_item(value, arg):
    try:
        return value[arg]
    except (IndexError, TypeError):
        return None
    
@register.filter
def to_range(value):
    return range(value)

@register.filter
def strip_tags(value):
    return re.sub(r'<[^>]*?>', '', value)