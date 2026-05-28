from django.urls import path
from . import views

app_name = 'booking'

urlpatterns = [
    # Bus Search
    path('search/', views.search_bus_view, name='search_bus'),
    path('bus-details/<int:schedule_id>/', views.bus_details_view, name='bus_details'),
    path('select-seats/<int:schedule_id>/', views.select_seats_view, name='select_seats'),
    
    # Booking Process
    path('passenger-details/', views.passenger_details_view, name='passenger_details'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('process-payment/', views.process_payment_view, name='process_payment'),
    path('confirmation/<uuid:booking_id>/', views.booking_confirmation_view, name='booking_confirmation'),
    
    # Booking Management
    path('history/', views.booking_history_view, name='booking_history'),
    path('detail/<uuid:booking_id>/', views.booking_detail_view, name='booking_detail'),
    path('cancel/<uuid:booking_id>/', views.cancel_booking_view, name='cancel_booking'),
    path('download-ticket/<uuid:booking_id>/', views.download_ticket_view, name='download_ticket'),
    
    # Ticket Verification
    path('verify-ticket/<str:ticket_number>/', views.verify_ticket_view, name='verify_ticket'),
]
