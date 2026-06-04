from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator

from item.models import Item, Category


@login_required
def index(request):
    items = Item.objects.filter(created_by=request.user)
    categories = Category.objects.all()
    favorites = request.user.favorite_items.all()

    return render(request, 'dashboard/index.html', {
        'items': items,
        'categories': categories,
        'favorites': favorites,
    })


def user_items(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    items_list = Item.objects.filter(created_by=user, is_sold=False)
    paginator = Paginator(items_list, 12)
    items = paginator.get_page(request.GET.get('page'))

    return render(request, 'dashboard/user_items.html', {
        'profile_user': user,
        'items': items,
    })
