#!/usr/bin/env python
"""
Create Hubli to Dharwad specific route and sample data for BRTS system
Run this script to add the specific route and related buses, schedules, and stops
"""

import os
import sys
import django

# Add project path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'brts_project.settings')
django.setup()

from bus_management.models import Route, Bus, Schedule, Stop
from django.utils import timezone
from datetime import datetime, timedelta

def create_hubli_dharwad_data():
    """Create Hubli to Dharwad specific route and sample data"""
    print("Creating Hubli to Dharwad route and related data...")
    
    # Create Hubli to Dharwad route
    route_data = {
        'name': 'Hubli to Dharwad',
        'source': 'Hubli',
        'destination': 'Dharwad',
        'distance': 280,
        'estimated_time': 360,  # 6 hours in minutes
        'base_fare': 800,
        'is_active': True
    }
    
    route, created = Route.objects.get_or_create(
        name=route_data['name'],
        defaults=route_data
    )
    
    if created:
        print(f"✓ Created route: {route.name}")
    else:
        print(f"- Route already exists: {route.name}")
    
    # Create specific buses for Hubli to Dharwad route
    buses_data = [
        {
            'bus_number': 'MH-01-HD-1111',
            'bus_type': 'volvo',
            'capacity': 45,
            'driver_name': 'Rajesh Kumar',
            'driver_phone': '9876543211',
            'registration_number': 'MH01HD1111',
            'amenities': ['WiFi', 'Charging Points', 'Blankets', 'Water Bottle', 'Entertainment System', 'Emergency Exit'],
            'status': 'active'
        },
        {
            'bus_number': 'MH-01-HD-2222',
            'bus_type': 'volvo',
            'capacity': 50,
            'driver_name': 'Sanjay Patil',
            'driver_phone': '9876543212',
            'registration_number': 'MH01HD2222',
            'amenities': ['WiFi', 'Charging Points', 'Blankets', 'Water Bottle', 'Entertainment System', 'Emergency Exit'],
            'status': 'active'
        },
        {
            'bus_number': 'MH-02-DW-3333',
            'bus_type': 'ac',
            'capacity': 40,
            'driver_name': 'Amit Sharma',
            'driver_phone': '9876543213',
            'registration_number': 'MH02DW3333',
            'amenities': ['WiFi', 'Charging Points', 'Water Bottle', 'Emergency Exit'],
            'status': 'active'
        }
    ]
    
    created_buses = []
    for bus_data in buses_data:
        bus_data['route'] = route
        bus, created = Bus.objects.get_or_create(
            bus_number=bus_data['bus_number'],
            defaults=bus_data
        )
        created_buses.append(bus)
        if created:
            print(f"✓ Created bus: {bus.bus_number} for route {route.name}")
        else:
            print(f"- Bus already exists: {bus.bus_number}")
    
    # Create schedules for Hubli to Dharwad route
    tomorrow = timezone.now() + timedelta(days=1)
    
    # Multiple departure times throughout the day
    departure_times = [
        tomorrow.replace(hour=6, minute=0, second=0, microsecond=0),
        tomorrow.replace(hour=8, minute=30, second=0, microsecond=0),
        tomorrow.replace(hour=11, minute=0, second=0, microsecond=0),
        tomorrow.replace(hour=14, minute=30, second=0, microsecond=0),
        tomorrow.replace(hour=17, minute=0, second=0, microsecond=0),
        tomorrow.replace(hour=20, minute=0, second=0, microsecond=0),
        tomorrow.replace(hour=22, minute=30, second=0, microsecond=0),
    ]
    
    for i, departure_time in enumerate(departure_times):
        for j, bus in enumerate(created_buses):
            arrival_time = departure_time + timedelta(hours=6)  # 6 hours travel time
            
            schedule, created = Schedule.objects.get_or_create(
                route=route,
                bus=bus,
                departure_time=departure_time.time(),
                defaults={
                    'arrival_time': arrival_time.time(),
                    'frequency': 'Daily',
                    'days_of_week': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'],
                    'effective_from': tomorrow.date(),
                    'is_active': True
                }
            )
            if created:
                print(f"✓ Created schedule for {route.name} at {departure_time.strftime('%H:%M')}")
    
    # Create specific stops for Hubli to Dharwad route
    stops_data = [
        {'name': 'Hubli Bus Stand', 'location': 'Hubli, Maharashtra'},
        {'name': 'Lonavala', 'location': 'Lonavala, Maharashtra'},
        {'name': 'Pune', 'location': 'Pune, Maharashtra'},
        {'name': 'Mumbai', 'location': 'Mumbai, Maharashtra'},
        {'name': 'Dharwad', 'location': 'Dharwad, Maharashtra'},
    ]
    
    for stop_data in stops_data:
        stop, created = Stop.objects.get_or_create(
            name=stop_data['name'],
            defaults=stop_data
        )
        if created:
            print(f"✓ Created stop: {stop.name}")
        else:
            print(f"- Stop already exists: {stop.name}")
    
    print("\n✅ Hubli to Dharwad route and data created successfully!")
    print("\n🚌 Available buses for Hubli to Dharwad:")
    for bus in created_buses:
        print(f"  • {bus.bus_number} ({bus.bus_type}) - {bus.capacity} seats")
    
    print("\n🕐 Schedule times:")
    for schedule in Schedule.objects.filter(route=route):
        print(f"  • {schedule.departure_time.strftime('%H:%M')} - Arrival: {schedule.arrival_time.strftime('%H:%M')}")
    
    print("\n📍 Available stops:")
    for stop in Stop.objects.all():
        print(f"  • {stop.name} - {stop.location}")
    
    print("\n🎯 Testing Instructions:")
    print("  1. Go to: http://127.0.0.1:8000/booking/search/")
    print("  2. Search for: Hubli to Dharwad")
    print("  3. Select tomorrow's date")
    print("  4. You should see 4 buses with different departure times")
    print("  5. Click on any bus to view details and proceed with booking")

if __name__ == '__main__':
    create_hubli_dharwad_data()
