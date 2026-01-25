from django import template

register = template.Library()


@register.filter
def ru_plural(value, forms):
    """
    forms: 'продукт,продукта,продуктов'
    """
    try:
        value = abs(int(value))
    except (TypeError, ValueError):
        return ''

    one, two, five = forms.split(',')

    if value % 10 == 1 and value % 100 != 11:
        return one
    elif 2 <= value % 10 <= 4 and not (12 <= value % 100 <= 14):
        return two
    else:
        return five
