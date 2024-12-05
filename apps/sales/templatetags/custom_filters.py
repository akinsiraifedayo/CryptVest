from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def currency(value):
    try:
        value = float(value)
        return mark_safe(f"$ {value:,.2f}")
    except (ValueError, TypeError):
        return "$ 0.00"

@register.filter
def get_price(package, account_type):
    return package.get_price(account_type)
