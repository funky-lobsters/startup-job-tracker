from django import forms
from django.contrib.auth.forms import BaseUserCreationForm

from .models import User


class SignUpForm(BaseUserCreationForm):
    class Meta:
        model = User
        fields = ("email",)

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email
