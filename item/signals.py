from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Category
from .views import CATEGORY_CACHE_KEY


@receiver(post_save, sender=Category)
@receiver(post_delete, sender=Category)
def invalidate_category_cache(sender, **kwargs):
    cache.delete(CATEGORY_CACHE_KEY)
