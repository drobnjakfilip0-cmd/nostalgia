from django.shortcuts import render, redirect
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from item.models import Item, Category
from .forms import ProfileForm, SignupForm

User = get_user_model()


def index(request):
    items = Item.objects.filter(is_sold=False)
    categories = Category.objects.all()
    return render(request, 'core/index.html', {
        'items': items,
        'categories': categories,
    })


def contact(request):
    return render(request, 'core/contact.html')


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            activation_link = request.build_absolute_uri(f"/activate/{uid}/{token}/")

            html_content = render_to_string(
                'core/email/activation_email.html',
                {'activation_link': activation_link},
            )

            email = EmailMultiAlternatives(
                subject="Aktivacija naloga",
                body="Aktiviraj nalog klikom na link.",
                from_email=None,
                to=[user.email],
            )
            email.attach_alternative(html_content, "text/html")
            email.send()

            return render(request, 'core/activation_sent.html', {'email': user.email})

    else:
        form = SignupForm()

    return render(request, 'core/signup.html', {'form': form})


def activate_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
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


@login_required
def edit_profile(request):
    profile = request.user.profile

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile, user=request.user)

        if form.is_valid():
            form.save()
            return redirect('dashboard:index')

    else:
        form = ProfileForm(instance=profile, user=request.user)

    return render(request, 'core/edit_profile.html', {'form': form})
