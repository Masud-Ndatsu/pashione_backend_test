from django.urls import path, re_path
from . import views


urlpatterns = [
    path("register/", views.register_user, name="register_user"),
    path("login/", views.login_user, name="login_user"),
    path("profile/", views.get_user_profile, name="get_user_profile"),
]