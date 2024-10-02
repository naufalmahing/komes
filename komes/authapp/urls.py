from django.urls import path, include
from django.contrib.auth import views as authviews
from . import views

urlpatterns = [
    path('login/', authviews.LoginView.as_view(template_name='authapp/login.html', next_page='/komes/'), name='login'),
    path('logout/', authviews.LogoutView.as_view(template_name='authapp/logout.html', next_page='/accounts/login/'), name='logout'),
    path('password_change/', authviews.PasswordResetView.as_view(template_name='authapp/password_change.html'), name='password_reset'),
    path('register/', views.RegisterView.as_view(template_name='authapp/register.html'), name='register'),

]