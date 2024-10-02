from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import forms as authforms
from django.contrib.auth.hashers import make_password

class RegisterForm(authforms.AuthenticationForm):
    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        user = User.objects.create(username=username, password=make_password(password))
        user.save()
        self.user_cache = user
        return self.cleaned_data