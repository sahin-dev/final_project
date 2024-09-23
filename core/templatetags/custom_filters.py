# core/templatetags/custom_filters.py
from django import template
from datetime import datetime

register = template.Library()

@register.filter
def remaining_life(mfd, life):
    if not mfd or not life:
        return ("Unknown", "text-muted")  # Return a default value if data is missing

    try:
        life_days = int(life.split()[0])
    except (ValueError, IndexError):
        return ("Unknown", "text-muted")  # Return a default value if parsing fails

    mfd_date = mfd.date()
    today = datetime.now().date()

    remaining_days = life_days - (today - mfd_date).days

    if remaining_days <= 0:
        return ("Expired", "text-danger")
    
    return (f"{remaining_days} Day{'s' if remaining_days > 1 else ''}", "text-success")
