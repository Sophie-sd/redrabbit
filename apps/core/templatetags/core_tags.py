"""
Template tags для Core контенту
"""
from django import template
from apps.core.models import TrackingPixel

register = template.Library()


@register.simple_tag
def get_tracking_pixels():
    """Отримати активні tracking pixels"""
    return TrackingPixel.objects.filter(is_active=True).select_related()

