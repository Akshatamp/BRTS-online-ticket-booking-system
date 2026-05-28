from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from bus_management.models import Route, Bus, Schedule, Stop
from accounts.models import User


class Command(BaseCommand):
    help = 'Create sample data for BRTS system'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create sample routes
        routes_data = [
            {
                'name': 'Mumbai to Pune',
                'source': 'Mumbai',
                'destination': 'Pune',
                'distance': 150,
                'estimated_time': 210,  # 3h 30m = 210 minutes
                'base_fare': 500,
                'is_active': True
            },
            {
                'name': 'Pune to Mumbai',
                'source': 'Pune',
                'destination': 'Mumbai',
                'distance': 150,
                'estimated_time': 210,  # 3h 30m = 210 minutes
                'base_fare': 500,
                'is_active': True
            },
            {
                'name': 'Mumbai to Nashik',
                'source': 'Mumbai',
                'destination': 'Nashik',
                'distance': 180,
                'estimated_time': 240,  # 4h 00m = 240 minutes
                'base_fare': 600,
                'is_active': True
            },
            {
                'name': 'Nashik to Mumbai',
                'source': 'Nashik',
                'destination': 'Mumbai',
                'distance': 180,
                'estimated_time': 240,  # 4h 00m = 240 minutes
                'base_fare': 600,
                'is_active': True
            },
            {
                'name': 'Mumbai to Ahmedabad',
                'source': 'Mumbai',
                'destination': 'Ahmedabad',
                'distance': 530,
                'estimated_time': 480,  # 8h 00m = 480 minutes
                'base_fare': 1200,
                'is_active': True
            }
        ]
        
        created_routes = []
        for route_data in routes_data:
            route, created = Route.objects.get_or_create(
                name=route_data['name'],
                defaults=route_data
            )
            created_routes.append(route)
            if created:
                self.stdout.write(f'Created route: {route.name}')
        
        # Create sample buses
        buses_data = [
            {
                'bus_number': 'MH-01-AB-1234',
                'bus_type': 'ac',
                'capacity': 40,
                'driver_name': 'Ramesh Kumar',
                'driver_phone': '9876543210',
                'registration_number': 'MH01AB1234',
                'amenities': ['WiFi', 'Charging Points', 'Water Bottle'],
                'status': 'active'
            },
            {
                'bus_number': 'MH-01-CD-5678',
                'bus_type': 'volvo',
                'capacity': 30,
                'driver_name': 'Suresh Sharma',
                'driver_phone': '9876543211',
                'registration_number': 'MH01CD5678',
                'amenities': ['WiFi', 'Charging Points', 'Blankets', 'Water Bottle'],
                'status': 'active'
            },
            {
                'bus_number': 'MH-01-EF-9012',
                'bus_type': 'standard',
                'capacity': 45,
                'driver_name': 'Mohan Singh',
                'driver_phone': '9876543212',
                'registration_number': 'MH01EF9012',
                'amenities': ['Charging Points', 'Water Bottle'],
                'status': 'active'
            }
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
                self.stdout.write(f'Created bus: {bus.bus_number} for route {route.name}')
        
        # Create sample schedules
        tomorrow = timezone.now() + timedelta(days=1)
        
        for i, route in enumerate(created_routes):
            for j, bus in enumerate(created_buses[:2]):  # Use first 2 buses for each route
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
                        'effective_from': tomorrow.date(),
                        'is_active': True
                    }
                )
                if created:
                    self.stdout.write(f'Created schedule for {route.name} at {departure_time.strftime("%H:%M")}')
        
        # Create sample stops
        stops_data = [
            {'name': 'Mumbai Central', 'location': 'Mumbai, Maharashtra'},
            {'name': 'Pune Station', 'location': 'Pune, Maharashtra'},
            {'name': 'Nashik Stand', 'location': 'Nashik, Maharashtra'},
            {'name': 'Ahmedabad Terminal', 'location': 'Ahmedabad, Gujarat'},
            {'name': 'Thane', 'location': 'Thane, Maharashtra'},
            {'name': 'Lonavala', 'location': 'Lonavala, Maharashtra'}
        ]
        
        for stop_data in stops_data:
            stop, created = Stop.objects.get_or_create(
                name=stop_data['name'],
                defaults=stop_data
            )
            if created:
                self.stdout.write(f'Created stop: {stop.name}')
        
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
