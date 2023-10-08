from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class UserRegisterForm(UserCreationForm):
    full_phone = forms.CharField(
        required=True
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2', 'full_phone']
