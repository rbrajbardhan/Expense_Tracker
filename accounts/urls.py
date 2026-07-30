from django.urls import path
from .views import SignUpView, UserLoginView, UserLogoutView, profile_view, CustomPasswordChangeView

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('profile/', profile_view, name='profile'),
    path('password-change/', CustomPasswordChangeView.as_view(), name='password_change'),
]
