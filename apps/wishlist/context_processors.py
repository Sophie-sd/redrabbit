"""
Context processors для wishlist
"""
from .wishlist import Wishlist


def wishlist(request):
    """Додає wishlist в контекст всіх шаблонів"""
    return {
        'wishlist': Wishlist(request),
        'wishlist_count': len(Wishlist(request))
    }

