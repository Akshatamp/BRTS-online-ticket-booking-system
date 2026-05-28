from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Profile Management
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('profile/update/', views.update_profile_view, name='update_profile'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Password Management
    path('change-password/', views.CustomPasswordChangeView.as_view(), name='change_password'),
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset-done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset-password-confirm/<str:token>/', views.reset_password_confirm_view, name='reset_password_confirm'),
]
