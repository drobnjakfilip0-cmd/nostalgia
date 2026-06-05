from django.shortcuts import render, redirect
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, logout
from django.views.decorators.http import require_POST
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django_ratelimit.decorators import ratelimit

from item.models import Item, Category
from item.views import _get_categories
from .forms import ProfileForm, SignupForm

User = get_user_model()


# ── 429 handlers ──────────────────────────────────────────────────────────────

def ratelimited(request, exception):
    return render(request, 'core/429.html', status=429)


def locked_out(request, credentials, *args, **kwargs):
    return render(request, 'core/429.html', status=429)


# ── Public views ──────────────────────────────────────────────────────────────

def index(request):
    items = (
        Item.objects.filter(is_sold=False)
            .select_related('category', 'created_by')
            .order_by('-created_at')[:6]
    )
    categories = _get_categories()
    return render(request, 'core/index.html', {
        'items': items,
        'categories': categories,
    })


def contact(request):
    return render(request, 'core/contact.html')


@ratelimit(key='ip', rate='10/h', method='POST', block=True)
def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            uid   = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            activation_link = request.build_absolute_uri(f'/activate/{uid}/{token}/')

            html_content = render_to_string(
                'core/email/activation_email.html',
                {'activation_link': activation_link},
            )

            email = EmailMultiAlternatives(
                subject='Aktivacija naloga',
                body='Aktiviraj nalog klikom na link.',
                from_email=None,
                to=[user.email],
            )
            email.attach_alternative(html_content, 'text/html')
            email.send()

            return render(request, 'core/activation_sent.html', {'email': user.email})

    else:
        form = SignupForm()

    return render(request, 'core/signup.html', {'form': form})


def activate_account(request, uidb64, token):
    try:
        uid  = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('core:login')

    return redirect('core:signup')


class CustomPasswordResetView(PasswordResetView):
    email_template_name = 'core/email/password_reset_email.html'

    def dispatch(self, request, *args, **kwargs):
        from django_ratelimit.core import is_ratelimited
        limited = is_ratelimited(
            request,
            fn=self.dispatch,
            key='ip',
            rate='5/h',
            method='POST',
            increment=request.method == 'POST',
        )
        if limited:
            return render(request, 'core/429.html', status=429)
        return super().dispatch(request, *args, **kwargs)


# ── Authenticated views ────────────────────────────────────────────────────────

@login_required
def edit_profile(request):
    from core.models import Profile
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile, user=request.user)

        if form.is_valid():
            form.save()
            return redirect('dashboard:index')

    else:
        form = ProfileForm(instance=profile, user=request.user)

    return render(request, 'core/edit_profile.html', {'form': form})


@require_POST
@login_required
def deactivate_account(request):
    user = request.user
    logout(request)
    # Mark inactive — email stays in DB but clean_email now allows re-registration
    user.is_active = False
    user.save()
    return redirect('core:index')
