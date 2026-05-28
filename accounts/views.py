from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.views import PasswordChangeView, PasswordResetView
from django.utils.decorators import method_decorator
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db import transaction
import uuid

from .forms import (
    CustomUserCreationForm, UserLoginForm, UserProfileForm,
    UserProfileExtendedForm, CustomPasswordChangeForm, CustomPasswordResetForm
)
from .models import User, UserProfile, PasswordReset


def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('bus_management:admin_dashboard')
        return redirect('core:home')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save(commit=False)
                user.is_active = True
                user.save()
                
                # Create user profile
                UserProfile.objects.create(user=user)
                
                # Send welcome email
                try:
                    send_mail(
                        'Welcome to BRTS Online Ticket Booking',
                        f'Dear {user.get_full_name()},\n\nWelcome to BRTS Online Ticket Booking System! Your account has been successfully created.\n\nThank you for choosing us!\n\nBest regards,\nBRTS Team',
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        fail_silently=True,
                    )
                except:
                    pass
                
                messages.success(request, 'Registration successful! You can now login.')
                return redirect('accounts:login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('bus_management:admin_dashboard')
        return redirect('core:home')
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data.get('remember_me')
            
            # Try to authenticate using email as username directly
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                
                # Set session expiration based on remember me
                if not remember_me:
                    request.session.set_expiry(0)  # Browser session
                
                messages.success(request, f'Welcome back, {user.get_full_name()}!')
                if user.is_staff:
                    next_url = request.GET.get('next', 'bus_management:admin_dashboard')
                else:
                    next_url = request.GET.get('next', 'core:home')
                return redirect(next_url)
            else:
                # If direct email authentication fails, try to find user by email and authenticate with username
                try:
                    user_obj = User.objects.get(email=email)
                    user = authenticate(request, username=user_obj.username, password=password)
                    
                    if user is not None:
                        login(request, user)
                        
                        # Set session expiration based on remember me
                        if not remember_me:
                            request.session.set_expiry(0)  # Browser session
                        
                        messages.success(request, f'Welcome back, {user.get_full_name()}!')
                        if user.is_staff:
                            next_url = request.GET.get('next', 'bus_management:admin_dashboard')
                        else:
                            next_url = request.GET.get('next', 'core:home')
                        return redirect(next_url)
                    else:
                        messages.error(request, 'Invalid email or password.')
                except User.DoesNotExist:
                    messages.error(request, 'Invalid email or password.')
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """User logout view"""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('core:home')


@login_required
def profile_view(request):
    """User profile view"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Get user statistics
    from booking.models import Booking
    total_bookings = Booking.objects.filter(user=request.user).count()
    upcoming_journeys = Booking.objects.filter(
        user=request.user,
        booking_status='confirmed',
        travel_date__gte=timezone.now().date()
    ).count()
    
    context = {
        'profile': profile,
        'total_bookings': total_bookings,
        'upcoming_journeys': upcoming_journeys,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile_view(request):
    """Edit user profile view"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        profile_form = UserProfileExtendedForm(request.POST, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            with transaction.atomic():
                user_form.save()
                profile_form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('accounts:profile')
    else:
        user_form = UserProfileForm(instance=request.user)
        profile_form = UserProfileExtendedForm(instance=profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def update_profile_view(request):
    """Update user profile view"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        profile_form = UserProfileExtendedForm(request.POST, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            with transaction.atomic():
                user_form.save()
                profile_form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('accounts:profile')
    else:
        user_form = UserProfileForm(instance=request.user)
        profile_form = UserProfileExtendedForm(instance=profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'accounts/edit_profile.html', context)


class CustomPasswordChangeView(PasswordChangeView):
    """Custom password change view"""
    form_class = CustomPasswordChangeForm
    template_name = 'accounts/change_password.html'
    success_url = reverse_lazy('accounts:profile')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Password changed successfully!')
        return response


class CustomPasswordResetView(PasswordResetView):
    """Custom password reset view"""
    form_class = CustomPasswordResetForm
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('accounts:password_reset_done')
    
    def form_valid(self, form):
        email = form.cleaned_data['email']
        try:
            user = User.objects.get(email=email)
            # Create password reset token
            token = str(uuid.uuid4())
            PasswordReset.objects.create(user=user, token=token)
            
            # Send password reset email
            reset_url = f"{self.request.scheme}://{self.request.get_host()}/accounts/reset-password-confirm/{token}/"
            
            try:
                send_mail(
                    'Password Reset Request',
                    f'Hi {user.get_full_name()},\n\nYou requested a password reset for your BRTS account.\n\nClick the link below to reset your password:\n{reset_url}\n\nThis link will expire in 24 hours.\n\nIf you didn\'t request this, please ignore this email.\n\nBest regards,\nBRTS Team',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=True,
                )
            except:
                pass
        except User.DoesNotExist:
            # Don't reveal if email exists or not
            pass
        
        messages.success(self.request, 'Password reset link has been sent to your email.')
        return redirect(self.success_url)


def reset_password_confirm_view(request, token):
    """Password reset confirmation view"""
    try:
        password_reset = PasswordReset.objects.get(token=token, is_used=False)
        
        # Check if token is still valid (24 hours)
        if (timezone.now() - password_reset.created_at).total_seconds() > 86400:
            messages.error(request, 'Password reset link has expired.')
            return redirect('accounts:login')
        
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            if new_password and confirm_password and new_password == confirm_password:
                password_reset.user.set_password(new_password)
                password_reset.user.save()
                
                # Mark token as used
                password_reset.is_used = True
                password_reset.save()
                
                messages.success(request, 'Password reset successfully! You can now login with your new password.')
                return redirect('accounts:login')
            else:
                messages.error(request, 'Passwords do not match.')
        
        return render(request, 'accounts/reset_password_confirm.html', {'token': token})
        
    except PasswordReset.DoesNotExist:
        messages.error(request, 'Invalid password reset link.')
        return redirect('accounts:login')


@login_required
def dashboard_view(request):
    """User dashboard view"""
    from booking.models import Booking, Notification
    
    # Get recent bookings
    recent_bookings = Booking.objects.filter(
        user=request.user
    ).order_by('-booking_date')[:5]
    
    # Get upcoming journeys
    upcoming_journeys = Booking.objects.filter(
        user=request.user,
        booking_status='confirmed',
        travel_date__gte=timezone.now().date()
    ).order_by('travel_date')[:3]
    
    # Get unread notifications
    unread_notifications = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).order_by('-created_at')[:5]
    
    # Get statistics
    total_bookings = Booking.objects.filter(user=request.user).count()
    completed_journeys = Booking.objects.filter(
        user=request.user,
        booking_status='completed'
    ).count()
    cancelled_bookings = Booking.objects.filter(
        user=request.user,
        booking_status='cancelled'
    ).count()
    
    context = {
        'recent_bookings': recent_bookings,
        'upcoming_journeys': upcoming_journeys,
        'unread_notifications': unread_notifications,
        'total_bookings': total_bookings,
        'completed_journeys': completed_journeys,
        'cancelled_bookings': cancelled_bookings,
    }
    return render(request, 'accounts/dashboard.html', context)
