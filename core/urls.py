from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import LoginForm
from django.urls import reverse_lazy
from .forms import CustomSetPasswordForm
from .views import CustomPasswordResetView


app_name = 'core'

urlpatterns=[
    path('', views.index, name='index'),
    path('contact/', views.contact, name='contact'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html', authentication_form=LoginForm), name='login'),
      # PASSWORD RESET - ENTER EMAIL
path(
    'password-reset/',
    CustomPasswordResetView.as_view(
        template_name='core/password_reset.html',
        email_template_name='core/email/password_reset_email.html',
        html_email_template_name = 'core/email/password_reset_email.html',
        success_url=reverse_lazy('core:password_reset_done')
    ),
    name='password_reset'
),

    # EMAIL SENT
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='core/password_reset_done.html'
        ),
        name='password_reset_done'
    ),

    # LINK FROM EMAIL
   path(
    'reset/<uidb64>/<token>/',
    auth_views.PasswordResetConfirmView.as_view(
        template_name='core/password_reset_confirm.html',
        success_url=reverse_lazy('core:password_reset_complete'),
         form_class=CustomSetPasswordForm
    ),
    name='password_reset_confirm'
),

    # SUCCESS
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='core/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate'),

    path('profile/edit/', views.edit_profile, name='edit_profile')
]
    
    
    
    
