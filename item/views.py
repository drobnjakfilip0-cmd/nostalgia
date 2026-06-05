from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from .forms import EditItemForm, NewItemForm, SIZE_CHOICES
from .models import Category, Item, ItemImage, ItemSize

CATEGORY_CACHE_KEY = 'all_categories'
CATEGORY_CACHE_TTL = 300


def _get_categories():
    categories = cache.get(CATEGORY_CACHE_KEY)
    if categories is None:
        categories = list(Category.objects.annotate(item_count=Count('items')))
        cache.set(CATEGORY_CACHE_KEY, categories, CATEGORY_CACHE_TTL)
    return categories


def items(request):
    query       = request.GET.get('query', '')
    category_id = request.GET.get('category', '')

    categories = _get_categories()
    qs = (
        Item.objects.filter(is_sold=False)
            .select_related('category', 'created_by')
            .prefetch_related('favorites')
            .order_by('-created_at')
    )

    if category_id and category_id != '0':
        qs = qs.filter(category_id=category_id)

    if query:
        qs = qs.filter(Q(name__icontains=query) | Q(description__icontains=query))

    page_obj = Paginator(qs, 12).get_page(request.GET.get('page'))

    return render(request, 'item/items.html', {
        'items':       page_obj,
        'page_obj':    page_obj,
        'query':       query,
        'categories':  categories,
        'category_id': category_id,
    })


def detail(request, pk):
    item = get_object_or_404(
        Item.objects.select_related('category', 'created_by')
                    .prefetch_related('images', 'available_sizes'),
        pk=pk,
    )
    related_items = (
        Item.objects.filter(category=item.category, is_sold=False)
                    .exclude(pk=pk)
                    .select_related('category', 'created_by')[:6]
    )
    # All possible sizes come from SIZE_CHOICES (single source of truth in forms.py)
    # Available sizes for THIS item come from the ItemSize records in the DB
    available_sizes = list(item.available_sizes.values_list('size', flat=True))
    return render(request, 'item/detail.html', {
        'item':            item,
        'related_items':   related_items,
        'all_sizes':       [value for value, label in SIZE_CHOICES],
        'available_sizes': available_sizes,
    })


def seller(request, pk):
    user = get_object_or_404(User, pk=pk)
    return render(request, 'item/seller.html', {'user': user})


@login_required
def new(request):
    if not request.user.profile.can_sell:
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = NewItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.created_by = request.user
            item.save()  # item now has a PK

            # sizes saved AFTER item.save() so item.pk exists
            sizes = form.cleaned_data.get('sizes')
            if sizes:
                ItemSize.objects.bulk_create([
                    ItemSize(item=item, size=s, stock=1) for s in sizes
                ])

            images = request.FILES.getlist('images')
            if images:
                ItemImage.objects.bulk_create([
                    ItemImage(item=item, image=img) for img in images
                ])
            return redirect('item:detail', pk=item.id)
    else:
        form = NewItemForm()

    return render(request, 'item/form.html', {'form': form})


@login_required
def edit(request, pk):
    item = get_object_or_404(Item, pk=pk, created_by=request.user)

    if request.method == 'POST':
        print("DEBUG POST sizes:", request.POST.getlist('sizes'))
        form = EditItemForm(request.POST, request.FILES, instance=item)
        print("DEBUG form valid:", form.is_valid())
        print("DEBUG form errors:", form.errors)
        if form.is_valid():
            print("DEBUG cleaned sizes:", form.cleaned_data.get('sizes'))
            item = form.save()

            # replace sizes with the new selection
            sizes = form.cleaned_data.get('sizes')
            item.available_sizes.all().delete()
            if sizes:
                ItemSize.objects.bulk_create([
                    ItemSize(item=item, size=s, stock=1) for s in sizes
                ])
            print("DEBUG saved sizes:", list(item.available_sizes.values_list('size', flat=True)))

            images = request.FILES.getlist('images')
            if images:
                ItemImage.objects.bulk_create([
                    ItemImage(item=item, image=img) for img in images
                ])
            return redirect('item:detail', pk=item.id)
    else:
        form = EditItemForm(instance=item)

    return render(request, 'item/form.html', {'form': form})


@require_POST
@login_required
def delete(request, pk):
    item = get_object_or_404(Item, pk=pk, created_by=request.user)
    item.delete()
    return redirect('dashboard:index')


@require_POST
@login_required
def toggle_favorite(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if item.favorites.filter(pk=request.user.pk).exists():
        item.favorites.remove(request.user)
    else:
        item.favorites.add(request.user)
    return redirect(request.META.get('HTTP_REFERER', '/'))


@require_POST
def buy_now(request, pk):
    item = get_object_or_404(Item, pk=pk)

    if item.is_sold:
        return redirect('item:detail', pk=item.id)

    email = request.POST.get('email', '').strip()
    size  = request.POST.get('size')

    if not email:
        return redirect('item:detail', pk=item.id)

    html_content = render_to_string(
        'item/payment_email.html',
        {'item': item, 'size': size, 'buyer_email': email},
    )

    # 1. Buyer receives payment instructions
    msg_buyer = EmailMultiAlternatives(
        subject=f"Kupovina potvrda - {item.name}",
        body="Kupovina potvrda",
        to=[email],
    )
    msg_buyer.attach_alternative(html_content, 'text/html')
    msg_buyer.send()

    # 2. Seller is notified that someone wants to buy
    seller_email = item.created_by.email
    if seller_email:
        seller_html = render_to_string(
            'item/seller_notification_email.html',
            {'item': item, 'size': size, 'buyer_email': email},
        )
        msg_seller = EmailMultiAlternatives(
            subject=f"Nova kupovina - {item.name}",
            body="Neko želi da kupi tvoj dres.",
            to=[seller_email],
        )
        msg_seller.attach_alternative(seller_html, 'text/html')
        msg_seller.send()

    return redirect('item:detail', pk=item.id)
