from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model for BRTS system"""
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class UserProfile(models.Model):
    """Extended user profile information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True, null=True)
    preferences = models.JSONField(default=dict, blank=True)
    notification_settings = models.JSONField(default=dict, blank=True)
    travel_history_count = models.PositiveIntegerField(default=0)
    total_bookings = models.PositiveIntegerField(default=0)
    loyalty_points = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Profile of {self.user.get_full_name()}"


class PasswordReset(models.Model):
    """Password reset tokens"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"Password reset for {self.user.email}"

    def is_valid(self):
        from datetime import timedelta
        from django.utils import timezone
        return not self.is_used and (timezone.now() - self.created_at) < timedelta(hours=24)
