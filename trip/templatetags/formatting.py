from django import template

register = template.Library()

@register.filter(name="k")
def thousands_to_k(value):
    try:
        if value is None or value == "":
            return "?"
        n = int(value)
        # Round to nearest thousand and render as k with no decimals
        return f"{int(round(n / 1000.0))}k"
    except Exception:
        return value

