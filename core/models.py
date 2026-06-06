from django.contrib.auth.models import User
from django.db import models
from django import forms
from django.core.exceptions import ValidationError

MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB

def validate_image_size(image):
    if image.size > MAX_IMAGE_SIZE:
        raise ValidationError(
            "Slika ne sme biti veća od 5 MB."
        )

class Profile(models.Model):
    user     = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar   = models.ImageField(upload_to='avatars/', blank=True, null=True, validators=[validate_image_size])
    can_sell = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    @property
    def role(self):
        if self.user.is_staff:
            return 'admin'
        elif self.can_sell:
            return 'seller'
        return 'buyer'

    @property
    def role_display(self):
        return {'admin': 'Admin', 'seller': 'Seller', 'buyer': 'Buyer'}[self.role]

    @property
    def role_color(self):
        return {
            'admin':  '#7c3aed',  # purple
            'seller': '#c2410c',  # orange
            'buyer':  '#374151',  # gray
        }[self.role]
