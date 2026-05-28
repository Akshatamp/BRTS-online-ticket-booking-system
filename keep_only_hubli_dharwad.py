#!/usr/bin/env python
"""
Keep only Hubli to Dharwad route and remove all other routes
Run this script to clean up the database and keep only the Hubli to Dharwad route
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

def keep_only_hubli_dharwad():
    """Keep only Hubli to Dharwad route and remove all other routes"""
    print("Keeping only Hubli to Dharwad route and removing all other routes...")
    
    # Keep Hubli to Dharwad route
    hubli_route = Route.objects.filter(name='Hubli to Dharwad').first()
    if hubli_route:
        print(f"✓ Keeping Hubli to Dharwad route (ID: {hubli_route.id})")
    else:
        print("⚠️ Hubli to Dharwad route not found, creating it...")
        hubli_route = Route.objects.create(
            name='Hubli to Dharwad',
            source='Hubli',
            destination='Dharwad',
            distance=280,
            estimated_time=360,
            base_fare=800,
            is_active=True
        )
        print(f"✓ Created Hubli to Dharwad route (ID: {hubli_route.id})")
    
    # Delete all other routes
    other_routes = Route.objects.exclude(name='Hubli to Dharwad')
    deleted_count = other_routes.count()
    
    if deleted_count > 0:
        print(f"🗑️ Deleting {deleted_count} other routes...")
        for route in other_routes:
            print(f"  • Deleting: {route.name}")
            # Delete associated schedules first
            Schedule.objects.filter(route=route).delete()
            # Delete associated buses
            Bus.objects.filter(route=route).delete()
            route.delete()
        
        print(f"✅ Successfully deleted {deleted_count} routes")
    else:
        print("ℹ️ No other routes to delete")
    
    # Summary
    total_routes = Route.objects.count()
    print(f"\n📊 Route Summary:")
    print(f"  • Total routes: {total_routes}")
    print(f"  • Hubli to Dharwad: 1 route")
    
    if total_routes == 1:
        print("\n✅ Database cleanup completed! Only Hubli to Dharwad route remains.")
    else:
        print(f"\n⚠️ Expected 1 route, but found {total_routes} routes. Please check manually.")

if __name__ == '__main__':
    keep_only_hubli_dharwad()
