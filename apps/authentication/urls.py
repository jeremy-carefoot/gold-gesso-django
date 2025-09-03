from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from . import api_views

app_name = "authentication"

urlpatterns = [
    path("register/", api_views.RegisterView.as_view(), name="register"),
    path("login/", api_views.LoginView.as_view(), name="login"),
    path("logout/", api_views.LogoutView.as_view(), name="logout"),
    path("user/", api_views.UserProfileView.as_view(), name="user_profile"),
    path("password/change/", api_views.change_password, name="change_password"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]