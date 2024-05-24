from django import template
register = template.Library()

@register.filter
def get_item(list, index):
    if index < len(list):
        return list[index]
    else:
        return None