"""
Custom template filters для products
"""
from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Отримує елемент зі словника за ключем"""
    if dictionary:
        return dictionary.get(key)
    return None

