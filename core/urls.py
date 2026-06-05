from django.urls import path
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from . import views
from .forms import CustomPasswordResetForm, CustomSetPasswordForm, LoginForm
from .views import CustomPasswordResetView

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('contact/', views.contact, name='contact'),
    path('signup/', views.signup, name='signup'),
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='core/login.html',
            authentication_form=LoginForm,
        ),
        name='login',
    ),
    path(
        'password-reset/',
        CustomPasswordResetView.as_view(
            template_name='core/password_reset.html',
            email_template_name='core/email/password_reset_email.html',
            html_email_template_name='core/email/password_reset_email.html',
            form_class=CustomPasswordResetForm,
            success_url=reverse_lazy('core:password_reset_done'),
        ),
        name='password_reset',
    ),
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(template_name='core/password_reset_done.html'),
        name='password_reset_done',
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='core/password_reset_confirm.html',
            form_class=CustomSetPasswordForm,
            success_url=reverse_lazy('core:password_reset_complete'),
        ),
        name='password_reset_confirm',
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(template_name='core/password_reset_complete.html'),
        name='password_reset_complete',
    ),
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate'),
    path('profil/uredi/', views.edit_profile, name='edit_profile'),
    path('profil/deaktiviraj/', views.deactivate_account, name='deactivate_account'),
]
