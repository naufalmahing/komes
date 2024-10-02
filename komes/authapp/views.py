from django.shortcuts import render
from django.contrib.auth import views as authviews
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect 

from .forms import RegisterForm

class RegisterView(authviews.LoginView):
    template_name = 'authapp/register.html'
    next_page = '/accounts/login'
    authentication_form = RegisterForm
      
    def form_valid(self, form):
        return HttpResponseRedirect(self.get_success_url())
 
