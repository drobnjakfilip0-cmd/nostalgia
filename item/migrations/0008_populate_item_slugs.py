"""
Data migration: populate slug for every existing Item.
Runs generate_unique_slug so duplicates get -1, -2 suffixes.
"""
from django.db import migrations


def populate_slugs(apps, schema_editor):
    from item.models import generate_unique_slug   # uses live model helpers

    Item = apps.get_model('item', 'Item')

    for item in Item.objects.filter(slug='').order_by('id'):
        # We need to call generate_unique_slug with the live model
        # because the historical model from apps registry won't have it.
        # Re-implement the logic inline to be safe with historical models.
        from django.utils.text import slugify

        _SR_MAP = str.maketrans({
            'č': 'c', 'ć': 'c', 'š': 's', 'ž': 'z', 'đ': 'dj',
            'Č': 'C', 'Ć': 'C', 'Š': 'S', 'Ž': 'Z', 'Đ': 'Dj',
        })

        base = slugify(item.name.translate(_SR_MAP))[:50] or 'dres'
        slug = base
        counter = 1

        while Item.objects.filter(slug=slug).exists():
            slug = f"{base}-{counter}"
            counter += 1

        item.slug = slug
        item.save()


def reverse_slugs(apps, schema_editor):
    Item = apps.get_model('item', 'Item')
    Item.objects.all().update(slug='')


class Migration(migrations.Migration):

    dependencies = [
        ('item', '0007_add_item_slug'),
    ]

    operations = [
        migrations.RunPython(populate_slugs, reverse_slugs),
    ]
