#!/usr/bin/env python
"""
Restore the bus_management/models.py file to working state
This script will restore the original models.py file with proper imports
"""

import os
import sys

# Add project path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def restore_models_file():
    """Restore the models.py file to working state"""
    models_file = os.path.join(os.path.dirname(__file__), 'bus_management', 'models.py')
    
    print("Restoring bus_management/models.py to working state...")
    
    # Create the original working models.py content
    original_content = """from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class Route(models.Model):
    \"\"\"Bus route information\"\"\"
    name = models.CharField(max_length=100)
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    distance = models.FloatField(help_text="Distance in kilometers")
    estimated_time = models.IntegerField(help_text="Estimated travel time in minutes")
    base_fare = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Route"
        verbose_name_plural = "Routes"
    
    def __str__(self):
        return self.name


class Bus(models.Model):
    \"\"\"Bus information\"\"\"
    bus_number = models.CharField(max_length=20, unique=True)
    bus_type = models.CharField(max_length=10, choices=[
        ('ac', 'AC'),
        ('volvo', 'Volvo'),
        ('non_ac', 'Non-AC'),
    ])
    capacity = models.IntegerField(validators=[MinValueValidator(1)])
    driver_name = models.CharField(max_length=100)
    driver_phone = models.CharField(max_length=15)
    registration_number = models.CharField(max_length=20, unique=True)
    amenities = models.JSONField(default=list)
    status = models.CharField(max_length=10, choices=[
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Under Maintenance'),
    ], default='active')
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='buses')
    
    class Meta:
        verbose_name = "Bus"
        verbose_name_plural = "Buses"
    
    def __str__(self):
        return f"Bus {self.bus_number} - {self.route}"

    def get_available_seats(self, schedule_id):
        \"\"\"Get available seats for a specific schedule\"\"\"
        from booking.models import Booking
        
        schedule = Schedule.objects.get(id=schedule_id)
        booked_seats = Booking.objects.filter(
            schedule=schedule,
            seat_number__isnull=False
        ).values_list('seat_number', flat=True)
        
        total_capacity = self.capacity
        available_seats = total_capacity - len(booked_seats)
        
        return {
            'total_capacity': total_capacity,
            'booked_seats': booked_seats,
            'available_seats': available_seats
        }


class Schedule(models.Model):
    \"\"\"Bus schedule information\"\"\"
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='schedules')
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='schedules')
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    frequency = models.CharField(max_length=50, choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('custom', 'Custom'),
    ], default='daily')
    days_of_week = models.JSONField(default=list)
    effective_from = models.DateField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Schedule"
        verbose_name_plural = "Schedules"
    
    def __str__(self):
        return f"{self.bus.bus_number} - {self.route} ({self.departure_time})"


class Stop(models.Model):
    \"\"\"Bus stop information\"\"\"
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Stop"
        verbose_name_plural = "Stops"
    
    def __str__(self):
        return self.name


class Maintenance(models.Model):
    \"\"\"Bus maintenance records\"\"\"
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='maintenance_records')
    maintenance_type = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    performed_by = models.CharField(max_length=100)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Maintenance"
        verbose_name_plural = "Maintenance Records"
    
    def __str__(self):
        return f"{self.bus.bus_number} - {self.maintenance_type}"
"""
    
    # Write the restored content to file
    with open(models_file, 'w', encoding='utf-8') as f:
        f.write(original_content)
    
    print("✅ Successfully restored bus_management/models.py!")
    print("\n📝️ Changes made:")
    print("  • Restored original working models.py file")
    print("  • Fixed all import issues")
    print("  • Booking import is properly placed in get_available_seats method")
    print("\n🔄 Please restart Django server for changes to take effect.")

if __name__ == '__main__':
    restore_models_file()
