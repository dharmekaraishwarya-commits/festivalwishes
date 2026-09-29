
from django import template


register = template.Library()


# ============================================================
# GET ITEM FROM DICTIONARY
# ============================================================

@register.filter
def get_item(dictionary, key):

    if dictionary is None:

        return []

    return dictionary.get(
        key,
        []
    )

