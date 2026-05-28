from django.urls import path
from . import views

app_name = 'bus_management'

urlpatterns = [
    # Admin Dashboard
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    
    # Bus Management
    path('manage-buses/', views.manage_buses_view, name='manage_buses'),
    path('add-bus/', views.add_bus_view, name='add_bus'),
    path('edit-bus/<int:bus_id>/', views.edit_bus_view, name='edit_bus'),
    path('delete-bus/<int:bus_id>/', views.delete_bus_view, name='delete_bus'),
    
    # Route Management
    path('manage-routes/', views.manage_routes_view, name='manage_routes'),
    path('add-route/', views.add_route_view, name='add_route'),
    path('edit-route/<int:route_id>/', views.edit_route_view, name='edit_route'),
    path('delete-route/<int:route_id>/', views.delete_route_view, name='delete_route'),
    
    # Schedule Management
    path('manage-schedules/', views.manage_schedules_view, name='manage_schedules'),
    path('add-schedule/', views.add_schedule_view, name='add_schedule'),
    
    # User Management
    path('manage-users/', views.manage_users_view, name='manage_users'),
    path('toggle-user/<int:user_id>/', views.toggle_user_status_view, name='toggle_user_status'),
    
    # Reports
    path('reports/', views.reports_view, name='reports'),
]
