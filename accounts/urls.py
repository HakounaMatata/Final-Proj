from django.urls import path
from .views import SignUpView, LoginView, ProfileView, DeactivateMeView,ChangePasswordView,PasswordForgotMagicLinkView,PasswordResetVerifyView,PasswordResetConfirmView

app_name = "accounts"

urlpatterns = [
    path("signup/",   SignUpView.as_view(),   name="signup"),
    path("login/",    LoginView.as_view(),    name="login"),
    path("profile/",  ProfileView.as_view(),  name="profile"),
    path("deactivate/", DeactivateMeView.as_view(), name="deactivate"),
    path("profile/change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("password/forgot/", PasswordForgotMagicLinkView.as_view(), name="password-forgot"),
    path("password/reset/verify/", PasswordResetVerifyView.as_view(), name="password-reset-verify"),
    path("password/reset/confirm/", PasswordResetConfirmView.as_view(), name="password-reset-confirm"),

]
