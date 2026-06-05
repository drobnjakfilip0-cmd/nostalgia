from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User


# Serbian special-character transliteration for clean ASCII slugs
_SR_MAP = str.maketrans({
    'č': 'c', 'ć': 'c', 'š': 's', 'ž': 'z', 'đ': 'dj',
    'Č': 'C', 'Ć': 'C', 'Š': 'S', 'Ž': 'Z', 'Đ': 'Dj',
})


def _base_slug(name: str, max_length: int = 50) -> str:
    """Transliterate Serbian chars then slugify, truncated to max_length."""
    return slugify(name.translate(_SR_MAP))[:max_length]


def generate_unique_slug(name: str, instance=None) -> str:
    """
    Build a URL-safe slug from name.
    If a duplicate exists append -1, -2, … until unique.
    Excludes `instance` itself when checking (safe for edits).
    """
    base = _base_slug(name) or 'dres'   # fallback if name is all special chars
    slug = base
    qs   = Item.objects.all()
    if instance and instance.pk:
        qs = qs.exclude(pk=instance.pk)

    counter = 1
    while qs.filter(slug=slug).exists():
        slug = f"{base}-{counter}"
        counter += 1

    return slug


class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Item(models.Model):
    category    = models.ForeignKey(Category, related_name='items', on_delete=models.CASCADE)
    name        = models.CharField(max_length=255)
    slug        = models.SlugField(max_length=60, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    price       = models.DecimalField(max_digits=10, decimal_places=0)
    image       = models.ImageField(upload_to='item_images', blank=True, null=True)
    favorites   = models.ManyToManyField(User, related_name='favorite_items', blank=True)
    is_sold     = models.BooleanField(default=False, db_index=True)
    created_by  = models.ForeignKey(User, related_name='items', on_delete=models.CASCADE)
    created_at  = models.DateTimeField(auto_now_add=True, db_index=True)

    def save(self, *args, **kwargs):
        # Generate slug on first save only — preserves URLs after rename
        if not self.slug:
            self.slug = generate_unique_slug(self.name, instance=self)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ItemImage(models.Model):
    item  = models.ForeignKey(Item, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='item_images')

    def __str__(self):
        return f"Image for {self.item.name}"


class ItemSize(models.Model):
    item  = models.ForeignKey(Item, related_name='available_sizes', on_delete=models.CASCADE)
    size  = models.CharField(max_length=10)
    stock = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.item.name} - {self.size}"
