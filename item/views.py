from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.core.paginator import Paginator
from django.db.models import Q
from django.template.loader import render_to_string

from .forms import EditItemForm, NewItemForm
from .models import Category, Item, ItemImage


def items(request):
    query = request.GET.get('query', '')
    category_id = request.GET.get('category', '')

    categories = Category.objects.all()
    qs = Item.objects.filter(is_sold=False)

    if category_id and category_id != '0':
        qs = qs.filter(category_id=category_id)

    if query:
        qs = qs.filter(Q(name__icontains=query) | Q(description__icontains=query))

    page_obj = Paginator(qs, 12).get_page(request.GET.get('page'))

    return render(request, 'item/items.html', {
        'items': page_obj,
        'page_obj': page_obj,
        'query': query,
        'categories': categories,
        'category_id': category_id,
    })


def detail(request, pk):
    item = get_object_or_404(Item, pk=pk)

    related_items = Item.objects.filter(category=item.category, is_sold=False).exclude(pk=pk)

    return render(request, 'item/detail.html', {
        'item': item,
        'related_items': related_items,
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
            item.save()

            for img in request.FILES.getlist('images'):
                ItemImage.objects.create(item=item, image=img)

            return redirect('item:detail', pk=item.id)

    else:
        form = NewItemForm()

    return render(request, 'item/form.html', {'form': form})


@login_required
def edit(request, pk):
    item = get_object_or_404(Item, pk=pk, created_by=request.user)

    if request.method == 'POST':
        form = EditItemForm(request.POST, request.FILES, instance=item)

        if form.is_valid():
            item = form.save()

            for image in request.FILES.getlist('images'):
                ItemImage.objects.create(item=item, image=image)

            return redirect('item:detail', pk=item.id)

    else:
        form = EditItemForm(instance=item)

    return render(request, 'item/form.html', {'form': form})


@login_required
def delete(request, pk):
    item = get_object_or_404(Item, pk=pk, created_by=request.user)
    item.delete()
    return redirect('dashboard:index')


@login_required
def toggle_favorite(request, pk):
    item = get_object_or_404(Item, pk=pk)

    if request.user in item.favorites.all():
        item.favorites.remove(request.user)
    else:
        item.favorites.add(request.user)

    return redirect(request.META.get('HTTP_REFERER', '/'))


def buy_now(request, pk):
    item = get_object_or_404(Item, pk=pk)

    if request.method == 'POST':
        email = request.POST.get('email')
        size = request.POST.get('size')

        html_content = render_to_string(
            'item/payment_email.html',
            {'item': item, 'size': size},
        )

        msg = EmailMultiAlternatives(
            subject=f"Kupovina potvrda - {item.name}",
            body="Kupovina potvrda",
            to=[email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()

    return redirect('item:detail', pk=item.id)
