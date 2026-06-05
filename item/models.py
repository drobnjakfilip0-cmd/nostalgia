from django.db import models
from django.contrib.auth.models import User


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
    description = models.TextField(blank=True, null=True)
    price       = models.DecimalField(max_digits=10, decimal_places=0)
    image       = models.ImageField(upload_to='item_images', blank=True, null=True)
    favorites   = models.ManyToManyField(User, related_name='favorite_items', blank=True)
    is_sold     = models.BooleanField(default=False, db_index=True)
    created_by  = models.ForeignKey(User, related_name='items', on_delete=models.CASCADE)
    created_at  = models.DateTimeField(auto_now_add=True, db_index=True)

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
