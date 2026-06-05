from django import template

register = template.Library()


@register.filter
def price_format(value):
    try:
        return f"{float(value):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except (ValueError, TypeError):
        return value
