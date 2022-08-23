from django.urls import path
from .views import CustomUserCreate, EmailVerification , LogInUser, ForgotPassword, \
    ResetPassword, PasswordResetCheck, LogOutUser,UserProfileView

app_name = 'usersapp'

urlpatterns = [
    path('register/', CustomUserCreate.as_view(), name='create_user'),
    path('email-verify/', EmailVerification.as_view(), name='email-verify'),
    path('log-in/', LogInUser.as_view(), name='log-in'),
    path('log-out/', LogOutUser.as_view(), name='log-out'),
    path('forgot-password/', ForgotPassword.as_view(), name='forgot-password'),
    path('password-reset-check/<uidb64>/<token>/', PasswordResetCheck.as_view(), name='password-reset-check'),
    path('password-reset/<uidb64>/<token>/', ResetPassword.as_view(), name='password-reset'),
    path('user-profile/<id>/', UserProfileView.as_view(), name='user-profile')
]

