from django import template
register = template.Library()

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