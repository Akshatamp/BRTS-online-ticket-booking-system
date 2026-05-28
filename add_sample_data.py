#!/usr/bin/env python
"""
Simple script to add sample data to BRTS system
Run this script to populate the database with sample buses, routes, and schedules
"""

import os
import sys
import django

# Add project path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'brts_project.settings')
django.setup()

from bus_management.models import Route, Bus, Schedule
from django.utils import timezone
from datetime import datetime, timedelta

def add_sample_data():
    """Add sample data to the database"""
    print("Adding sample data to BRTS system...")
    
    # Create sample routes
    routes_data = [
        {'name': 'Mumbai to Pune', 'source': 'Mumbai', 'destination': 'Pune', 'distance': 150, 'estimated_time': 210, 'base_fare': 500},
        {'name': 'Pune to Mumbai', 'source': 'Pune', 'destination': 'Mumbai', 'distance': 150, 'estimated_time': 210, 'base_fare': 500},
        {'name': 'Mumbai to Nashik', 'source': 'Mumbai', 'destination': 'Nashik', 'distance': 180, 'estimated_time': 240, 'base_fare': 600},
        {'name': 'Nashik to Mumbai', 'source': 'Nashik', 'destination': 'Mumbai', 'distance': 180, 'estimated_time': 240, 'base_fare': 600},
    ]
    
    created_routes = []
    for route_data in routes_data:
        route, created = Route.objects.get_or_create(
            name=route_data['name'],
            defaults=route_data
        )
        created_routes.append(route)
        if created:
            print(f"✓ Created route: {route.name}")
        else:
            print(f"- Route already exists: {route.name}")
    
    # Create sample buses
    buses_data = [
        {
            'bus_number': 'MH-01-AB-1234', 
            'bus_type': 'ac', 
            'capacity': 40, 
            'driver_name': 'Ramesh Kumar',
            'driver_phone': '9876543210',
            'registration_number': 'MH01AB1234',
            'amenities': ['WiFi', 'Charging Points']
        },
        {
            'bus_number': 'MH-01-CD-5678', 
            'bus_type': 'volvo', 
            'capacity': 35, 
            'driver_name': 'Suresh Sharma',
            'driver_phone': '9876543211',
            'registration_number': 'MH01CD5678',
            'amenities': ['WiFi', 'Charging Points', 'Blankets', 'AC']
        },
        {
            'bus_number': 'MH-01-EF-9012', 
            'bus_type': 'standard', 
            'capacity': 45, 
            'driver_name': 'Mohan Singh',
            'driver_phone': '9876543212',
            'registration_number': 'MH01EF9012',
            'amenities': ['Charging Points']
        },
    ]
    
    created_buses = []
    for i, bus_data in enumerate(buses_data):
        # Assign each bus to a route (cycle through routes)
        route = created_routes[i % len(created_routes)]
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
    
    # Create sample schedules
    tomorrow = timezone.now() + timedelta(days=1)
    
    for i, route in enumerate(created_routes):
        for j, bus in enumerate(created_buses[:2]):
            departure_time = tomorrow.replace(hour=6 + i*2, minute=0, second=0, microsecond=0)
            arrival_time = departure_time + timedelta(hours=3 + i)
            
            schedule, created = Schedule.objects.get_or_create(
                route=route,
                bus=bus,
                departure_time=departure_time.time(),
                defaults={
                    'arrival_time': arrival_time.time(),
                    'frequency': 'Daily',
                    'days_of_week': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'],
                    'effective_from': tomorrow.date()
                }
            )
            if created:
                print(f"✓ Created schedule for {route.name} at {departure_time.strftime('%H:%M')}")
            else:
                print(f"- Schedule already exists for {route.name} at {departure_time.strftime('%H:%M')}")
    
    print("\n✅ Sample data added successfully!")
    print("\nAvailable routes for testing:")
    for route in Route.objects.all():
        print(f"  • {route.source} to {route.destination} - ₹{route.base_fare}")
    
    print("\nYou can now test the bus search functionality:")
    print("  1. Go to /booking/search/")
    print("  2. Try searching for 'Mumbai' to 'Pune'")
    print("  3. Select tomorrow's date")
    print("  4. You should see available buses!")

if __name__ == '__main__':
    add_sample_data()
