from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from core.models import Profile
from item.models import Item
from item.views import _get_categories


@login_required
def index(request):
    items_qs  = Item.objects.filter(created_by=request.user).select_related('category')
    items     = Paginator(items_qs, 24).get_page(request.GET.get('page'))
    favorites = request.user.favorite_items.select_related('category').all()

    return render(request, 'dashboard/index.html', {
        'items':      items,
        'categories': _get_categories(),
        'favorites':  favorites,
    })


def user_items(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    items_list = (
        Item.objects.filter(created_by=user, is_sold=False)
                    .select_related('category')
    )
    items = Paginator(items_list, 12).get_page(request.GET.get('page'))
    return render(request, 'dashboard/user_items.html', {
        'profile_user': user,
        'items':        items,
    })


# ── Admin-only: user management ───────────────────────────────────────────────

@login_required
def users(request):
    if not request.user.is_staff:
        return HttpResponseForbidden()

    all_users = (
        User.objects.select_related('profile')
                    .order_by('-date_joined')
    )

    role_filter = request.GET.get('role', '')
    if role_filter == 'admin':
        all_users = all_users.filter(is_staff=True)
    elif role_filter == 'seller':
        all_users = all_users.filter(is_staff=False, profile__can_sell=True)
    elif role_filter == 'buyer':
        all_users = all_users.filter(is_staff=False, profile__can_sell=False)

    return render(request, 'dashboard/users.html', {
        'all_users':     all_users,
        'role_filter':   role_filter,
        'filter_options': [
            ('Svi', ''), ('Admin', 'admin'), ('Prodavac', 'seller'), ('Kupac', 'buyer')
        ],
    })


@require_POST
@login_required
def set_user_role(request, user_id):
    if not request.user.is_staff:
        return HttpResponseForbidden()

    target = get_object_or_404(User, pk=user_id)

    # Never allow an admin to change their own role — would lock them out
    if target.pk == request.user.pk:
        return redirect('dashboard:users')

    role = request.POST.get('role')
    if role not in ('admin', 'seller', 'buyer'):
        return redirect('dashboard:users')

    # Map role → (is_staff, can_sell)
    role_map = {
        'admin':  (True,  True),
        'seller': (False, True),
        'buyer':  (False, False),
    }
    is_staff, can_sell = role_map[role]

    # Only update the two auth fields — never touch password or other sensitive fields
    User.objects.filter(pk=target.pk).update(is_staff=is_staff, is_superuser=False)

    # Ensure the profile exists before touching it, then update can_sell
    profile, _ = Profile.objects.get_or_create(user=target)
    Profile.objects.filter(pk=profile.pk).update(can_sell=can_sell)

    return redirect('dashboard:users')
