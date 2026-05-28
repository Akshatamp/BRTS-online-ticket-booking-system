from django.contrib import admin
from .models import Route, Bus, Schedule, Stop, Driver, BusAssignment, FuelRecord, BusInspection, RouteStop, BusPerformance, Maintenance

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('name', 'source', 'destination', 'distance', 'estimated_time', 'base_fare', 'is_active')
    list_filter = ('is_active', 'source', 'destination')
    search_fields = ('name', 'source', 'destination')
    ordering = ('name',)

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'license_number', 'license_expiry', 'is_active')
    list_filter = ('is_active', 'date_joined')
    search_fields = ('name', 'phone', 'email', 'license_number')
    ordering = ('name',)

@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    list_display = ('bus_number', 'bus_type', 'capacity', 'driver', 'route', 'registration_number', 'status')
    list_filter = ('status', 'bus_type', 'route')
    search_fields = ('bus_number', 'registration_number', 'driver__name', 'route__name')
    ordering = ('bus_number',)
    raw_id_fields = ('driver', 'route')

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('route', 'bus', 'departure_time', 'arrival_time', 'frequency', 'effective_from', 'is_active')
    list_filter = ('is_active', 'frequency', 'route')
    search_fields = ('route__name', 'bus__bus_number')
    ordering = ('departure_time',)

@admin.register(Stop)
class StopAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'location')
    ordering = ('name',)

@admin.register(BusAssignment)
class BusAssignmentAdmin(admin.ModelAdmin):
    list_display = ('bus', 'driver', 'assigned_date', 'shift_start', 'shift_end', 'is_active')
    list_filter = ('is_active', 'assigned_date')
    search_fields = ('bus__bus_number', 'driver__name')
    ordering = ('-assigned_date',)

@admin.register(FuelRecord)
class FuelRecordAdmin(admin.ModelAdmin):
    list_display = ('bus', 'fuel_date', 'fuel_type', 'fuel_quantity', 'fuel_cost', 'odometer_reading', 'fuel_station')
    list_filter = ('fuel_type', 'fuel_date')
    search_fields = ('bus__bus_number', 'fuel_station')
    ordering = ('-fuel_date',)

@admin.register(BusInspection)
class BusInspectionAdmin(admin.ModelAdmin):
    list_display = ('bus', 'inspection_date', 'inspection_type', 'inspection_result', 'inspected_by', 'next_inspection_date')
    list_filter = ('inspection_type', 'inspection_result', 'inspection_date')
    search_fields = ('bus__bus_number', 'inspected_by')
    ordering = ('-inspection_date',)

@admin.register(RouteStop)
class RouteStopAdmin(admin.ModelAdmin):
    list_display = ('route', 'stop', 'sequence_number', 'distance_from_start', 'estimated_arrival', 'is_active')
    list_filter = ('is_active', 'route')
    search_fields = ('route__name', 'stop__name')
    ordering = ('route', 'sequence_number')

@admin.register(BusPerformance)
class BusPerformanceAdmin(admin.ModelAdmin):
    list_display = ('bus', 'record_date', 'total_km_driven', 'total_trips', 'total_passengers', 'total_revenue', 'fuel_consumed')
    list_filter = ('record_date',)
    search_fields = ('bus__bus_number',)
    ordering = ('-record_date',)

@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    list_display = ('bus', 'maintenance_type', 'start_date', 'end_date', 'performed_by', 'notes')
    list_filter = ('maintenance_type', 'start_date')
    search_fields = ('bus__bus_number', 'performed_by', 'notes')
    ordering = ('-start_date',)
