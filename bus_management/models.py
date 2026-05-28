from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class Route(models.Model):
    """Bus route information"""
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


class Driver(models.Model):
    """Driver information"""
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(blank=True, null=True)
    license_number = models.CharField(max_length=50, unique=True)
    license_expiry = models.DateField()
    address = models.TextField()
    date_joined = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Driver"
        verbose_name_plural = "Drivers"
    
    def __str__(self):
        return self.name


class Bus(models.Model):
    """Bus information"""
    bus_number = models.CharField(max_length=20, unique=True)
    bus_type = models.CharField(max_length=20, choices=[
        ('ac_seater', 'AC Seater'),
        ('ac_sleeper', 'AC Sleeper'),
        ('non_ac_seater', 'Non-AC Seater'),
        ('non_ac_sleeper', 'Non-AC Sleeper'),
        ('volvo', 'Volvo AC'),
    ])
    capacity = models.IntegerField(validators=[MinValueValidator(1)])
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True, related_name='buses')
    registration_number = models.CharField(max_length=20, unique=True)
    amenities = models.JSONField(default=list)
    status = models.CharField(max_length=15, choices=[
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
        """Get available seats for a specific schedule"""
        from booking.models import Booking
        
        schedule = Schedule.objects.get(id=schedule_id)
        # Use seat_numbers field instead of seat_number
        bookings = Booking.objects.filter(schedule=schedule)
        booked_seats = []
        for booking in bookings:
            if booking.seat_numbers:
                booked_seats.extend(booking.seat_numbers)
        
        total_capacity = self.capacity
        available_seats = total_capacity - len(booked_seats)
        
        return {
            'total_capacity': total_capacity,
            'booked_seats': booked_seats,
            'available_seats': available_seats
        }


class Schedule(models.Model):
    """Bus schedule information"""
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
    """Bus stop information"""
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Stop"
        verbose_name_plural = "Stops"
    
    def __str__(self):
        return self.name


class Maintenance(models.Model):
    """Bus maintenance records"""
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


class BusAssignment(models.Model):
    """Bus driver assignments"""
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='assignments')
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='assignments')
    assigned_date = models.DateField()
    shift_start = models.TimeField()
    shift_end = models.TimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Bus Assignment"
        verbose_name_plural = "Bus Assignments"
        unique_together = ['bus', 'driver', 'assigned_date']
    
    def __str__(self):
        return f"{self.bus.bus_number} - {self.driver.name} ({self.assigned_date})"


class FuelRecord(models.Model):
    """Bus fuel consumption records"""
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='fuel_records')
    fuel_date = models.DateField()
    fuel_type = models.CharField(max_length=20, choices=[
        ('diesel', 'Diesel'),
        ('petrol', 'Petrol'),
        ('cng', 'CNG'),
        ('electric', 'Electric'),
    ])
    fuel_quantity = models.FloatField(help_text="Fuel quantity in liters")
    fuel_cost = models.DecimalField(max_digits=10, decimal_places=2)
    odometer_reading = models.IntegerField(help_text="Odometer reading in km")
    fuel_station = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Fuel Record"
        verbose_name_plural = "Fuel Records"
        ordering = ['-fuel_date']
    
    def __str__(self):
        return f"{self.bus.bus_number} - {self.fuel_date} - {self.fuel_quantity}L"


class BusInspection(models.Model):
    """Bus inspection records"""
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='inspection_records')
    inspection_date = models.DateField()
    inspection_type = models.CharField(max_length=50, choices=[
        ('daily', 'Daily Check'),
        ('weekly', 'Weekly Inspection'),
        ('monthly', 'Monthly Inspection'),
        ('annual', 'Annual Inspection'),
    ])
    inspected_by = models.CharField(max_length=100)
    inspection_result = models.CharField(max_length=20, choices=[
        ('passed', 'Passed'),
        ('failed', 'Failed'),
        ('conditional', 'Conditional Pass'),
    ])
    issues_found = models.TextField(blank=True)
    next_inspection_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Bus Inspection"
        verbose_name_plural = "Bus Inspections"
        ordering = ['-inspection_date']
    
    def __str__(self):
        return f"{self.bus.bus_number} - {self.inspection_type} ({self.inspection_date})"


class RouteStop(models.Model):
    """Route stops mapping"""
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='route_stops')
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE, related_name='route_stops')
    sequence_number = models.IntegerField(help_text="Order of stops in the route")
    distance_from_start = models.FloatField(help_text="Distance from route start in km")
    estimated_arrival = models.TimeField(help_text="Estimated arrival time from start")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Route Stop"
        verbose_name_plural = "Route Stops"
        unique_together = ['route', 'stop']
        ordering = ['sequence_number']
    
    def __str__(self):
        return f"{self.route.name} - {self.stop.name} (Stop {self.sequence_number})"


class BusPerformance(models.Model):
    """Bus performance metrics"""
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='performance_records')
    record_date = models.DateField()
    total_km_driven = models.FloatField(help_text="Total kilometers driven")
    total_trips = models.IntegerField(help_text="Number of trips completed")
    total_passengers = models.IntegerField(help_text="Total passengers carried")
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, help_text="Total revenue generated")
    fuel_consumed = models.FloatField(help_text="Total fuel consumed in liters")
    average_speed = models.FloatField(help_text="Average speed in km/h")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Bus Performance"
        verbose_name_plural = "Bus Performance Records"
        ordering = ['-record_date']
        unique_together = ['bus', 'record_date']
    
    def __str__(self):
        return f"{self.bus.bus_number} - {self.record_date}"
    
    def fuel_efficiency(self):
        """Calculate fuel efficiency in km/l"""
        if self.fuel_consumed > 0:
            return self.total_km_driven / self.fuel_consumed
        return 0
    
    def revenue_per_km(self):
        """Calculate revenue per kilometer"""
        if self.total_km_driven > 0:
            return self.total_revenue / self.total_km_driven
        return 0
