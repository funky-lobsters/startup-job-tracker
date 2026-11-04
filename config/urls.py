from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from accounts import views as account_views
from core import views as core_views

urlpatterns = [
    path("", core_views.home, name="home"),
    path("signup/", account_views.signup, name="signup"),
    path("login/", auth_views.LoginView.as_view(redirect_authenticated_user=True), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("admin/", admin.site.urls),
]
