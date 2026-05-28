#!/usr/bin/env python
"""
Fix the missing Booking import in bus_management/models.py
This script adds the missing import to fix the bus details error
"""

import os
import sys

# Add project path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def fix_booking_import():
    """Add the missing Booking import to bus_management/models.py"""
    models_file = os.path.join(os.path.dirname(__file__), 'bus_management', 'models.py')
    
    print("Fixing Booking import in bus_management/models.py...")
    
    # Read the current file content
    with open(models_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if Booking import already exists
    if 'from booking.models import Booking' in content:
        print("✓ Booking import already exists")
        return
    
    # Find the import section and add Booking import
    lines = content.split('\n')
    new_lines = []
    
    for line in lines:
        new_lines.append(line)
        # Add Booking import after the User model import
        if 'User = get_user_model()' in line:
            new_lines.append('from booking.models import Booking')
            print("✓ Added Booking import")
            break
    
    # Write the updated content back to file
    with open(models_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print("✅ Successfully fixed Booking import!")
    print("\n📝️ Changes made:")
    print("  • Added 'from booking.models import Booking' after User model import")
    print("\n🔄 Please restart the Django server for changes to take effect.")

if __name__ == '__main__':
    fix_booking_import()
