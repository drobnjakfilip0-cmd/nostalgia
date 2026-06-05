from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm,
    SetPasswordForm,
    UserCreationForm,
)
from django.contrib.auth.models import User

from .models import Profile

INPUT_CLASSES = (
    "w-full px-4 py-3 rounded-xl border border-black/10 "
    "focus:outline-none focus:ring-2 focus:ring-[#c2410c] bg-white"
)


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Your username', 'class': INPUT_CLASSES})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Your password', 'class': INPUT_CLASSES})
    )


class SignupForm(UserCreationForm):
    class Meta:
        model  = User
        fields = ('username', 'email', 'password1', 'password2')

    username  = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Your username', 'class': INPUT_CLASSES})
    )
    email     = forms.CharField(
        widget=forms.EmailInput(attrs={'placeholder': 'Your email address', 'class': INPUT_CLASSES})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Your password', 'class': INPUT_CLASSES})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Repeat password', 'class': INPUT_CLASSES})
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        # Only block if an ACTIVE account already uses this email.
        # Deactivated accounts free up their email for re-registration.
        if User.objects.filter(email=email, is_active=True).exists():
            raise forms.ValidationError('Profil sa ovim emailom već postoji.')
        return email


class CustomPasswordResetForm(PasswordResetForm):
    """Allow password reset for inactive users too."""
    def get_users(self, email):
        return User.objects.filter(email__iexact=email)


class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Unesi novu lozinku'})
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Ponovi lozinku'})
    )


class ProfileForm(forms.ModelForm):
    username = forms.CharField()

    class Meta:
        model  = Profile
        fields = ['avatar']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['username'].initial = self.user.username

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError('Ovo korisničko ime je zauzeto.')
        return username

    def save(self, commit=True):
        profile = super().save(commit=False)
        self.user.username = self.cleaned_data['username']
        self.user.save()
        if commit:
            profile.save()
        return profile
