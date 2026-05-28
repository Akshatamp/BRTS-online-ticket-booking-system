from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db import transaction
import json
from datetime import datetime, timedelta

from bus_management.models import Route, Bus, Schedule
from .models import Booking, Payment, Ticket, Notification
from .forms import BookingForm, PassengerDetailsForm


def create_sample_data():
    """Create sample data for testing"""
    from django.utils import timezone
    
    # Create sample routes
    routes_data = [
        {'name': 'Mumbai to Pune', 'source': 'Mumbai', 'destination': 'Pune', 'distance': 150, 'estimated_time': 210, 'base_fare': 500},  # 3h 30m = 210 minutes
        {'name': 'Pune to Mumbai', 'source': 'Pune', 'destination': 'Mumbai', 'distance': 150, 'estimated_time': 210, 'base_fare': 500},  # 3h 30m = 210 minutes
        {'name': 'Mumbai to Nashik', 'source': 'Mumbai', 'destination': 'Nashik', 'distance': 180, 'estimated_time': 240, 'base_fare': 600},  # 4h 00m = 240 minutes
        {'name': 'Nashik to Mumbai', 'source': 'Nashik', 'destination': 'Mumbai', 'distance': 180, 'estimated_time': 240, 'base_fare': 600},  # 4h 00m = 240 minutes
    ]
    
    created_routes = []
    for route_data in routes_data:
        route, created = Route.objects.get_or_create(
            name=route_data['name'],
            defaults=route_data
        )
        created_routes.append(route)
    
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
    
    # Create sample schedules
    tomorrow = timezone.now() + timedelta(days=1)
    
    for i, route in enumerate(created_routes):
        for j, bus in enumerate(created_buses[:2]):
            departure_time = tomorrow.replace(hour=6 + i*2, minute=0, second=0, microsecond=0)
            arrival_time = departure_time + timedelta(hours=3 + i)
            
            Schedule.objects.get_or_create(
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


def search_bus_view(request):
    """Bus search view"""
    # Create sample data if no routes exist
    if Route.objects.count() == 0:
        create_sample_data()
    
    routes = Route.objects.filter(is_active=True)
    search_results = []
    
    if request.method == 'GET' and any(request.GET.get(key) for key in ['source', 'destination', 'date']):
        source = request.GET.get('source', '').strip()
        destination = request.GET.get('destination', '').strip()
        travel_date = request.GET.get('date')
        
        if source and destination and travel_date:
            # Find routes matching source and destination
            matching_routes = Route.objects.filter(
                Q(source__icontains=source) & Q(destination__icontains=destination),
                is_active=True
            )
            
            for route in matching_routes:
                # Get schedules for this route
                schedules = Schedule.objects.filter(
                    route=route,
                    is_active=True,
                    effective_from__lte=travel_date
                ).select_related('bus').order_by('departure_time')
                
                route_schedules = []
                for schedule in schedules:
                    # Check if schedule operates on the travel date
                    travel_day = datetime.strptime(travel_date, '%Y-%m-%d').weekday()
                    days_of_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                    day_name = days_of_week[travel_day]
                    
                    # Check if schedule operates on this day
                    operates_today = (
                        day_name in schedule.days_of_week or 
                        'daily' in schedule.frequency.lower() or
                        'all' in schedule.frequency.lower()
                    )
                    
                    if operates_today:
                        # Use bus capacity as available seats since no bookings exist yet
                        available_seats = schedule.bus.capacity
                        route_schedules.append({
                            'schedule': schedule,
                            'available_seats': available_seats,
                            'fare': route.base_fare,
                        })
                
                if route_schedules:
                    search_results.append({
                        'route': route,
                        'schedules': route_schedules,
                    })
    
    context = {
        'routes': routes,
        'search_results': search_results,
        'search_params': {
            'source': request.GET.get('source', ''),
            'destination': request.GET.get('destination', ''),
            'date': request.GET.get('date', ''),
        }
    }
    return render(request, 'booking/search_bus.html', context)


@login_required
def bus_details_view(request, schedule_id):
    """Bus details view"""
    schedule = get_object_or_404(Schedule, id=schedule_id, is_active=True)
    
    # Get available seats
    seats_info = schedule.bus.get_available_seats(schedule_id)
    
    # Get all seats for layout
    seat_numbers = [str(i) for i in range(1, schedule.bus.capacity + 1)]
    
    # Determine available seats
    available_seats = []
    for seat_num in seat_numbers:
        if seat_num not in seats_info['booked_seats']:
            available_seats.append(seat_num)
    
    context = {
        'schedule': schedule,
        'route': schedule.route,
        'bus': schedule.bus,
        'seat_numbers': seat_numbers,
        'available_seats': available_seats,
        'booked_seats': seats_info['booked_seats'],
        'total_seats': schedule.bus.capacity,
        'booked_seats_count': len(seats_info['booked_seats']),
        'available_seats_count': len(available_seats),
    }
    return render(request, 'booking/bus_details.html', context)


@login_required
def select_seats_view(request, schedule_id):
    """Seat selection view"""
    schedule = get_object_or_404(Schedule, id=schedule_id, is_active=True)
    
    if request.method == 'POST':
        selected_seats = request.POST.getlist('selected_seats')
        
        if not selected_seats:
            messages.error(request, 'Please select at least one seat.')
            return redirect('booking:bus_details', schedule_id=schedule_id)
        
        # Store selected seats in session
        request.session['selected_seats'] = selected_seats
        request.session['schedule_id'] = schedule_id
        
        return redirect('booking:passenger_details')
    
    # Get available seats
    seats_info = schedule.bus.get_available_seats(schedule_id)
    
    # Get all seats for layout
    all_seats = [str(i) for i in range(1, schedule.bus.capacity + 1)]
    
    # Create seat layout
    seat_layout = []
    seats_per_row = 4
    for i in range(0, len(all_seats), seats_per_row):
        row = []
        for seat_num in all_seats[i:i + seats_per_row]:
            row.append({
                'number': seat_num,
                'available': seat_num not in seats_info['booked_seats'],
            })
        seat_layout.append(row)
    
    # Count available seats
    available_seats_count = len([seat for seat in all_seats if seat not in seats_info['booked_seats']])
    
    context = {
        'schedule': schedule,
        'route': schedule.route,
        'bus': schedule.bus,
        'seat_layout': seat_layout,
        'available_seats_count': available_seats_count,
        'travel_date': request.session.get('travel_date', 'Tomorrow'),
    }
    return render(request, 'booking/select_seats.html', context)


@login_required
def passenger_details_view(request):
    """Passenger details view"""
    schedule_id = request.session.get('schedule_id')
    selected_seats = request.session.get('selected_seats', [])
    
    if not schedule_id or not selected_seats:
        messages.error(request, 'Please select seats first.')
        return redirect('booking:search_bus')
    
    schedule = get_object_or_404(Schedule, id=schedule_id)
    
    if request.method == 'POST':
        form = PassengerDetailsForm(request.POST)
        if form.is_valid():
            # Store passenger details in session
            request.session['passenger_details'] = form.cleaned_data
            
            return redirect('booking:checkout')
    else:
        # Pre-fill with user's data
        initial_data = {
            'passenger_name': request.user.get_full_name(),
            'passenger_email': request.user.email,
            'passenger_phone': request.user.phone_number,
        }
        form = PassengerDetailsForm(initial=initial_data)
    
    # Calculate total fare
    total_fare = schedule.route.base_fare * len(selected_seats)
    
    context = {
        'form': form,
        'schedule': schedule,
        'route': schedule.route,
        'bus': schedule.bus,
        'selected_seats': selected_seats,
        'total_fare': total_fare,
    }
    return render(request, 'booking/passenger_details.html', context)


@login_required
def checkout_view(request):
    """Checkout view"""
    schedule_id = request.session.get('schedule_id')
    selected_seats = request.session.get('selected_seats', [])
    passenger_details = request.session.get('passenger_details')
    
    if not all([schedule_id, selected_seats, passenger_details]):
        messages.error(request, 'Missing booking information.')
        return redirect('booking:search_bus')
    
    schedule = get_object_or_404(Schedule, id=schedule_id)
    total_fare = schedule.route.base_fare * len(selected_seats)
    
    context = {
        'schedule': schedule,
        'route': schedule.route,
        'bus': schedule.bus,
        'selected_seats': selected_seats,
        'passenger_details': passenger_details,
        'total_fare': total_fare,
    }
    return render(request, 'booking/checkout.html', context)


@login_required
@require_POST
def process_payment_view(request):
    """Process payment"""
    schedule_id = request.session.get('schedule_id')
    selected_seats = request.session.get('selected_seats', [])
    passenger_details = request.session.get('passenger_details')
    
    if not all([schedule_id, selected_seats, passenger_details]):
        return JsonResponse({'success': False, 'message': 'Missing booking information'})
    
    try:
        with transaction.atomic():
            schedule = get_object_or_404(Schedule, id=schedule_id)
            total_fare = schedule.route.base_fare * len(selected_seats)
            
            # Generate unique booking reference
            import uuid
            booking_ref = f"BRTS{uuid.uuid4().hex[:8].upper()}"
            
            # Create booking
            booking = Booking.objects.create(
                user=request.user,
                schedule=schedule,
                bus=schedule.bus,
                route=schedule.route,
                booking_reference=booking_ref,
                passenger_name=passenger_details['passenger_name'],
                passenger_email=passenger_details['passenger_email'],
                passenger_phone=passenger_details['passenger_phone'],
                passenger_age=passenger_details['passenger_age'],
                passenger_gender=passenger_details['passenger_gender'],
                seat_numbers=selected_seats,
                number_of_seats=len(selected_seats),
                total_fare=total_fare,
                travel_date=datetime.strptime(request.session.get('travel_date', str(timezone.now().date())), '%Y-%m-%d').date(),
                booking_status='confirmed',
                payment_status='paid',
            )
            
            # Create payment record
            payment = Payment.objects.create(
                booking=booking,
                amount=total_fare,
                payment_method='credit_card',  # Demo payment method
                payment_status='completed',
                completed_at=timezone.now(),
            )
            
            # Generate ticket
            ticket = Ticket.objects.create(booking=booking)
            ticket.generate_qr_code()
            
            # Create notification
            Notification.objects.create(
                user=request.user,
                title='Booking Confirmed',
                message=f'Your booking {booking.booking_reference} has been confirmed. Total amount: ₹{total_fare}',
                notification_type='booking',
                booking=booking,
            )
            
            # Clear session
            for key in ['schedule_id', 'selected_seats', 'passenger_details', 'travel_date']:
                if key in request.session:
                    del request.session[key]
            
            return JsonResponse({
                'success': True,
                'booking_id': booking.id,
                'booking_reference': booking.booking_reference,
                'redirect_url': f'/booking/confirmation/{booking.id}/'
            })
            
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
def booking_confirmation_view(request, booking_id):
    """Booking confirmation view"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # Generate ticket if not exists
    if not hasattr(booking, 'ticket'):
        ticket = Ticket.objects.create(booking=booking)
        ticket.generate_qr_code()
    
    context = {
        'booking': booking,
        'ticket': booking.ticket,
    }
    return render(request, 'booking/booking_confirmation.html', context)


def verify_ticket_view(request, ticket_number):
    """Verify ticket by scanning QR code"""
    try:
        ticket = get_object_or_404(Ticket, ticket_number=ticket_number)
        booking = ticket.booking
        
        context = {
            'ticket': ticket,
            'booking': booking,
            'is_valid': ticket.is_valid,
        }
        return render(request, 'booking/ticket_verification.html', context)
    except Exception as e:
        context = {
            'error': 'Ticket not found or invalid',
            'ticket_number': ticket_number,
        }
        return render(request, 'booking/ticket_verification.html', context)


@login_required
def booking_history_view(request):
    """Booking history view"""
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    
    # Pagination
    paginator = Paginator(bookings, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'booking/booking_history.html', context)


@login_required
def booking_detail_view(request, booking_id):
    """Booking detail view"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    context = {
        'booking': booking,
    }
    return render(request, 'booking/booking_detail.html', context)


@login_required
@require_POST
def cancel_booking_view(request, booking_id):
    """Cancel booking view"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if not booking.is_cancellable():
        messages.error(request, 'This booking cannot be cancelled.')
        return redirect('booking:booking_detail', booking_id=booking_id)
    
    try:
        with transaction.atomic():
            refund_amount = booking.calculate_refund_amount()
            
            booking.booking_status = 'cancelled'
            booking.cancellation_date = timezone.now()
            booking.cancellation_reason = request.POST.get('reason', 'Customer request')
            booking.refund_amount = refund_amount
            booking.save()
            
            # Update payment status
            if hasattr(booking, 'payment'):
                booking.payment.payment_status = 'refunded'
                booking.payment.refund_amount = refund_amount
                booking.payment.refund_date = timezone.now()
                booking.payment.save()
            
            # Create notification
            Notification.objects.create(
                user=request.user,
                title='Booking Cancelled',
                message=f'Your booking {booking.booking_reference} has been cancelled. Refund amount: ₹{refund_amount}',
                notification_type='cancellation',
                booking=booking,
            )
            
            messages.success(request, f'Booking cancelled successfully. Refund amount: ₹{refund_amount}')
            
    except Exception as e:
        messages.error(request, f'Error cancelling booking: {str(e)}')
    
    return redirect('booking:booking_detail', booking_id=booking_id)


@login_required
def download_ticket_view(request, booking_id):
    """Download ticket view"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if booking.booking_status != 'confirmed':
        messages.error(request, 'Ticket not available for this booking.')
        return redirect('booking:booking_detail', booking_id=booking_id)
    
    # Generate PDF ticket (simplified version)
    from django.http import HttpResponse
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch
    import io
    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Add content to PDF
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, "BRTS E-TICKET")
    
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 100, f"Booking Reference: {booking.booking_reference}")
    p.drawString(50, height - 120, f"Passenger: {booking.passenger_name}")
    p.drawString(50, height - 140, f"Route: {booking.route.source} to {booking.route.destination}")
    p.drawString(50, height - 160, f"Bus: {booking.bus.bus_number}")
    p.drawString(50, height - 180, f"Date: {booking.travel_date}")
    p.drawString(50, height - 200, f"Departure: {booking.schedule.departure_time}")
    p.drawString(50, height - 220, f"Seats: {', '.join(booking.seat_numbers)}")
    p.drawString(50, height - 240, f"Total Fare: ₹{booking.total_fare}")
    
    p.save()
    
    pdf = buffer.getvalue()
    buffer.close()
    
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_{booking.booking_reference}.pdf"'
    
    return response
