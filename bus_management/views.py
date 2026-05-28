from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum, Avg, Q
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.http import HttpResponse
from datetime import datetime, timedelta
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from .models import Route, Bus, Schedule, Stop, Driver, BusAssignment, FuelRecord, BusInspection, RouteStop, BusPerformance, Maintenance
from booking.models import Booking, Payment, Feedback
from core.models import ContactMessage
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

def is_admin(user):
    """Check if user is admin"""
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(is_admin)
def admin_dashboard_view(request):
    """Admin dashboard view"""
    # Get statistics
    total_users = User.objects.filter(is_active=True).count()
    total_bookings = Booking.objects.count()
    total_revenue = Payment.objects.filter(payment_status='completed').aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    total_buses = Bus.objects.count()
    active_buses = Bus.objects.filter(status='active').count()
    total_routes = Route.objects.filter(is_active=True).count()
    
    # Today's bookings
    today = timezone.now().date()
    today_bookings = Booking.objects.filter(booking_date__date=today).count()
    
    # Recent bookings
    recent_bookings = Booking.objects.select_related('user', 'route').order_by('-booking_date')[:10]
    
    # Most popular routes
    popular_routes = Route.objects.filter(
        is_active=True
    ).annotate(
        booking_count=Count('bookings')
    ).order_by('-booking_count')[:5]
    
    # Monthly revenue (last 6 months)
    monthly_revenue = []
    for i in range(6):
        month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
        month_end = month_start.replace(day=28) + timedelta(days=4)  # End of month
        month_revenue = Payment.objects.filter(
            payment_status='completed',
            payment_date__date__gte=month_start.date(),
            payment_date__date__lte=month_end.date()
        ).aggregate(total=Sum('amount'))['total'] or 0
        monthly_revenue.append({
            'month': month_start.strftime('%b %Y'),
            'revenue': float(month_revenue)
        })
    
    # Booking status distribution
    booking_stats = Booking.objects.values('booking_status').annotate(
        count=Count('id')
    ).order_by('booking_status')
    
    # Bus status distribution
    bus_stats = Bus.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    # Recent feedback
    recent_feedback = Feedback.objects.select_related('user').order_by('-created_at')[:5]
    
    # Unread messages
    unread_messages = ContactMessage.objects.filter(is_read=False).count()
    
    context = {
        'total_users': total_users,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'total_buses': total_buses,
        'active_buses': active_buses,
        'total_routes': total_routes,
        'today_bookings': today_bookings,
        'recent_bookings': recent_bookings,
        'popular_routes': popular_routes,
        'monthly_revenue': monthly_revenue,
        'booking_stats': booking_stats,
        'bus_stats': bus_stats,
        'recent_feedback': recent_feedback,
        'unread_messages': unread_messages,
    }
    return render(request, 'bus_management/admin_dashboard_simple.html', context)


@login_required
@user_passes_test(is_admin)
def manage_buses_view(request):
    """Manage buses view"""
    buses = Bus.objects.select_related('route').order_by('bus_number')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        buses = buses.filter(
            Q(bus_number__icontains=search_query) |
            Q(driver_name__icontains=search_query) |
            Q(route__source__icontains=search_query) |
            Q(route__destination__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        buses = buses.filter(status=status_filter)
    
    # Get statistics
    total_buses = Bus.objects.count()
    active_buses = Bus.objects.filter(status='active').count()
    maintenance_buses = Bus.objects.filter(status='maintenance').count()
    inactive_buses = Bus.objects.filter(status='inactive').count()
    
    # Pagination
    paginator = Paginator(buses, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get drivers and routes for dropdowns
    drivers = Driver.objects.filter(is_active=True)
    routes = Route.objects.filter(is_active=True)
    
    context = {
        'buses': page_obj,
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'total_buses': total_buses,
        'active_buses': active_buses,
        'maintenance_buses': maintenance_buses,
        'inactive_buses': inactive_buses,
        'drivers': drivers,
        'routes': routes,
    }
    return render(request, 'bus_management/bus_table.html', context)


@login_required
@user_passes_test(is_admin)
def add_bus_view(request):
    """Add bus view"""
    if request.method == 'POST':
        # Handle form submission
        bus_number = request.POST.get('bus_number')
        bus_type = request.POST.get('bus_type')
        capacity = request.POST.get('capacity')
        driver_name = request.POST.get('driver_name')
        driver_phone = request.POST.get('driver_phone')
        registration_number = request.POST.get('registration_number')
        route_id = request.POST.get('route')
        
        try:
            route = Route.objects.get(id=route_id)
            bus = Bus.objects.create(
                bus_number=bus_number,
                bus_type=bus_type,
                capacity=capacity,
                driver_name=driver_name,
                driver_phone=driver_phone,
                registration_number=registration_number,
                route=route
            )
            messages.success(request, f'Bus {bus_number} added successfully!')
            return redirect('bus_management:manage_buses')
        except Exception as e:
            messages.error(request, f'Error adding bus: {str(e)}')
    
    routes = Route.objects.filter(is_active=True)
    context = {
        'routes': routes,
    }
    return render(request, 'bus_management/add_bus.html', context)


@login_required
@user_passes_test(is_admin)
def edit_bus_view(request, bus_id):
    """Edit bus view"""
    bus = get_object_or_404(Bus, id=bus_id)
    
    if request.method == 'POST':
        # Handle form submission
        bus.bus_number = request.POST.get('bus_number')
        bus.bus_type = request.POST.get('bus_type')
        bus.capacity = request.POST.get('capacity')
        bus.driver_name = request.POST.get('driver_name')
        bus.driver_phone = request.POST.get('driver_phone')
        bus.registration_number = request.POST.get('registration_number')
        route_id = request.POST.get('route')
        
        try:
            route = Route.objects.get(id=route_id)
            bus.route = route
            bus.save()
            messages.success(request, f'Bus {bus.bus_number} updated successfully!')
            return redirect('bus_management:manage_buses')
        except Exception as e:
            messages.error(request, f'Error updating bus: {str(e)}')
    
    routes = Route.objects.filter(is_active=True)
    context = {
        'bus': bus,
        'routes': routes,
    }
    return render(request, 'bus_management/edit_bus.html', context)


@login_required
@user_passes_test(is_admin)
def delete_bus_view(request, bus_id):
    """Delete bus view"""
    if request.method == 'POST':
        bus = get_object_or_404(Bus, id=bus_id)
        
        try:
            bus_number = bus.bus_number
            bus.delete()
            messages.success(request, f'Bus {bus_number} deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error deleting bus: {str(e)}')
    
    return redirect('bus_management:manage_buses')


@login_required
@user_passes_test(is_admin)
def manage_routes_view(request):
    """Manage routes view"""
    routes = Route.objects.filter(is_active=True).order_by('source', 'destination')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        routes = routes.filter(
            Q(source__icontains=search_query) |
            Q(destination__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(routes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Add statistics
    total_routes = routes.count()
    active_routes = routes.filter(is_active=True).count()
    inactive_routes = routes.filter(is_active=False).count()
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'total_routes': total_routes,
        'active_routes': active_routes,
        'inactive_routes': inactive_routes,
    }
    return render(request, 'bus_management/manage_routes.html', context)


@login_required
@user_passes_test(is_admin)
def add_route_view(request):
    """Add route view"""
    if request.method == 'POST':
        # Handle form submission
        name = request.POST.get('name')
        source = request.POST.get('source')
        destination = request.POST.get('destination')
        distance = request.POST.get('distance')
        estimated_time = request.POST.get('estimated_time')
        base_fare = request.POST.get('base_fare')
        stops = request.POST.getlist('stops')
        
        try:
            route = Route.objects.create(
                name=name,
                source=source,
                destination=destination,
                distance=distance,
                estimated_time=estimated_time,
                base_fare=base_fare,
                stops=stops
            )
            messages.success(request, f'Route {source} to {destination} added successfully!')
            return redirect('bus_management:manage_routes')
        except Exception as e:
            messages.error(request, f'Error adding route: {str(e)}')
    
    return render(request, 'bus_management/add_route.html')


@login_required
@user_passes_test(is_admin)
def edit_route_view(request, route_id):
    """Edit route view"""
    route = get_object_or_404(Route, id=route_id)
    
    if request.method == 'POST':
        # Handle form submission
        route.name = request.POST.get('name')
        route.source = request.POST.get('source')
        route.destination = request.POST.get('destination')
        route.distance = request.POST.get('distance')
        route.estimated_time = request.POST.get('estimated_time')
        route.base_fare = request.POST.get('base_fare')
        stops = request.POST.getlist('stops')
        
        try:
            route.stops = stops
            route.save()
            messages.success(request, f'Route {route.source} to {route.destination} updated successfully!')
            return redirect('bus_management:manage_routes')
        except Exception as e:
            messages.error(request, f'Error updating route: {str(e)}')
    
    context = {
        'route': route,
    }
    return render(request, 'bus_management/edit_route.html', context)


@login_required
@user_passes_test(is_admin)
@require_POST
def delete_route_view(request, route_id):
    """Delete route view"""
    route = get_object_or_404(Route, id=route_id)
    
    try:
        route_name = f"{route.source} to {route.destination}"
        route.is_active = False
        route.save()
        messages.success(request, f'Route {route_name} deactivated successfully!')
    except Exception as e:
        messages.error(request, f'Error deactivating route: {str(e)}')
    
    return redirect('bus_management:manage_routes')


@login_required
@user_passes_test(is_admin)
def manage_schedules_view(request):
    """Manage schedules view"""
    schedules = Schedule.objects.select_related('bus', 'route').order_by('departure_time')
    
    # Filter by route
    route_filter = request.GET.get('route', '')
    if route_filter:
        schedules = schedules.filter(route_id=route_filter)
    
    # Pagination
    paginator = Paginator(schedules, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    routes = Route.objects.filter(is_active=True)
    
    # Add statistics
    total_schedules = schedules.count()
    active_schedules = schedules.filter(is_active=True).count()
    daily_schedules = schedules.filter(frequency='daily').count()
    weekly_schedules = schedules.filter(frequency='weekly').count()
    
    context = {
        'page_obj': page_obj,
        'routes': routes,
        'route_filter': route_filter,
        'total_schedules': total_schedules,
        'active_schedules': active_schedules,
        'daily_schedules': daily_schedules,
        'weekly_schedules': weekly_schedules,
    }
    return render(request, 'bus_management/manage_schedules.html', context)


@login_required
@user_passes_test(is_admin)
def add_schedule_view(request):
    """Add schedule view"""
    if request.method == 'POST':
        # Handle form submission
        bus_id = request.POST.get('bus')
        route_id = request.POST.get('route')
        departure_time = request.POST.get('departure_time')
        arrival_time = request.POST.get('arrival_time')
        frequency = request.POST.get('frequency')
        days_of_week = request.POST.getlist('days_of_week')
        effective_from = request.POST.get('effective_from')
        
        try:
            bus = Bus.objects.get(id=bus_id)
            route = Route.objects.get(id=route_id)
            schedule = Schedule.objects.create(
                bus=bus,
                route=route,
                departure_time=departure_time,
                arrival_time=arrival_time,
                frequency=frequency,
                days_of_week=days_of_week,
                effective_from=effective_from
            )
            messages.success(request, 'Schedule added successfully!')
            return redirect('bus_management:manage_schedules')
        except Exception as e:
            messages.error(request, f'Error adding schedule: {str(e)}')
    
    buses = Bus.objects.filter(status='active')
    routes = Route.objects.filter(is_active=True)
    
    context = {
        'buses': buses,
        'routes': routes,
    }
    return render(request, 'bus_management/add_schedule.html', context)


@login_required
@user_passes_test(is_admin)
def manage_users_view(request):
    """Manage users view"""
    users = User.objects.all().order_by('-date_joined')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    
    # Pagination
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Add statistics
    total_users = users.count()
    active_users = users.filter(is_active=True).count()
    staff_users = users.filter(is_staff=True).count()
    regular_users = users.filter(is_staff=False).count()
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'total_users': total_users,
        'active_users': active_users,
        'staff_users': staff_users,
        'regular_users': regular_users,
        'users': users,
    }
    return render(request, 'bus_management/manage_users.html', context)


@login_required
@user_passes_test(is_admin)
@require_POST
def toggle_user_status_view(request, user_id):
    """Toggle user status view"""
    user = get_object_or_404(User, id=user_id)
    
    try:
        user.is_active = not user.is_active
        user.save()
        status = 'activated' if user.is_active else 'deactivated'
        messages.success(request, f'User {user.get_full_name()} {status} successfully!')
    except Exception as e:
        messages.error(request, f'Error updating user status: {str(e)}')
    
    return redirect('bus_management:manage_users')


@login_required
@user_passes_test(is_admin)
def reports_view(request):
    """Reports view"""
    from datetime import datetime, timedelta
    from django.utils import timezone
    
    # Get date range
    start_date = request.GET.get('start_date') or request.GET.get('from')
    end_date = request.GET.get('end_date') or request.GET.get('to')
    report_type = request.GET.get('type', '')
    export_format = request.GET.get('export', '')
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    else:
        start_date = timezone.now().date() - timedelta(days=30)
    
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        end_date = timezone.now().date()
    
    # Adjust date range based on report type
    if report_type == 'daily':
        start_date = end_date = timezone.now().date()
    elif report_type == 'weekly':
        start_date = timezone.now().date() - timedelta(days=7)
    elif report_type == 'monthly':
        start_date = timezone.now().date() - timedelta(days=30)
    elif report_type == 'yearly':
        start_date = timezone.now().date() - timedelta(days=365)
    
    # Generate report data
    reports_data = []
    current_date = start_date
    
    while current_date <= end_date:
        day_bookings = Booking.objects.filter(
            booking_date__date=current_date
        ).select_related('route', 'bus')
        
        if day_bookings.exists():
            # Group by route for the day
            route_data = {}
            for booking in day_bookings:
                route_key = f"{booking.route.source} to {booking.route.destination}"
                if route_key not in route_data:
                    route_data[route_key] = {
                        'route': booking.route,
                        'bookings': [],
                        'revenue': 0,
                        'passengers': 0
                    }
                route_data[route_key]['bookings'].append(booking)
                route_data[route_key]['revenue'] += booking.total_fare or 0
                route_data[route_key]['passengers'] += booking.number_of_seats or 1
            
            for route_info in route_data.values():
                reports_data.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'route_name': f"{route_info['route'].source} to {route_info['route'].destination}",
                    'bus_number': route_info['route'].buses.first().bus_number if route_info['route'].buses.exists() else 'N/A',
                    'bookings_count': len(route_info['bookings']),
                    'revenue': route_info['revenue'],
                    'passengers_count': route_info['passengers']
                })
        
        current_date += timedelta(days=1)
    
    # Calculate totals
    total_bookings = Booking.objects.filter(
        booking_date__date__gte=start_date,
        booking_date__date__lte=end_date
    ).count()
    
    total_revenue = Booking.objects.filter(
        booking_date__date__gte=start_date,
        booking_date__date__lte=end_date
    ).aggregate(total=Sum('total_fare'))['total'] or 0
    
    # Calculate total passengers by summing number_of_seats
    bookings_for_passengers = Booking.objects.filter(
        booking_date__date__gte=start_date,
        booking_date__date__lte=end_date
    )
    total_passengers = 0
    for booking in bookings_for_passengers:
        total_passengers += booking.number_of_seats or 1
    if total_passengers == 0:
        total_passengers = total_bookings
    
    active_routes = Route.objects.filter(is_active=True).count()
    
    # Handle export
    if export_format == 'excel':
        return export_excel_report(reports_data, start_date, end_date, report_type)
    elif export_format == 'pdf':
        return export_pdf_report(reports_data, start_date, end_date, report_type)
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'date_from': start_date.strftime('%Y-%m-%d'),
        'date_to': end_date.strftime('%Y-%m-%d'),
        'reports': reports_data,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'total_passengers': total_passengers,
        'active_routes': active_routes,
        'booking_by_status': Booking.objects.filter(
            booking_date__date__gte=start_date,
            booking_date__date__lte=end_date
        ).values('booking_status').annotate(count=Count('id')).order_by('booking_status'),
        'revenue_by_route': Booking.objects.filter(
            booking_date__date__gte=start_date,
            booking_date__date__lte=end_date
        ).values('route__source', 'route__destination').annotate(
            revenue=Sum('total_fare'),
            count=Count('id')
        ).order_by('-revenue')[:10],
        'daily_bookings': [
            {
                'date': (start_date + timedelta(days=i)).strftime('%Y-%m-%d'),
                'count': Booking.objects.filter(
                    booking_date__date=start_date + timedelta(days=i)
                ).count()
            }
            for i in range((end_date - start_date).days + 1)
        ]
    }
    return render(request, 'bus_management/reports.html', context)


def export_excel_report(reports_data, start_date, end_date, report_type):
    """Export report to Excel format"""
    # Create workbook and worksheet
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "BRTS Report"
    
    # Define styles
    header_font = Font(bold=True, color='FFFFFF')
    header_fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
    header_alignment = Alignment(horizontal='center', vertical='center')
    
    # Add title
    ws.merge_cells('A1:F1')
    title_cell = ws['A1']
    title_cell.value = f"BRTS Booking Report - {report_type.title() if report_type else 'Custom'}"
    title_cell.font = Font(bold=True, size=16)
    title_cell.alignment = Alignment(horizontal='center')
    
    # Add date range
    ws.merge_cells('A2:F2')
    date_cell = ws['A2']
    date_cell.value = f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
    date_cell.font = Font(bold=True, size=12)
    date_cell.alignment = Alignment(horizontal='center')
    
    # Add headers
    headers = ['Date', 'Route', 'Bus Number', 'Bookings', 'Revenue (₹)', 'Passengers']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=4, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
    
    # Add data
    for row, report in enumerate(reports_data, 5):
        ws.cell(row=row, column=1, value=report['date'])
        ws.cell(row=row, column=2, value=report['route_name'])
        ws.cell(row=row, column=3, value=report['bus_number'])
        ws.cell(row=row, column=4, value=report['bookings_count'])
        ws.cell(row=row, column=5, value=report['revenue'])
        ws.cell(row=row, column=6, value=report['passengers_count'])
    
    # Add totals
    if reports_data:
        total_row = len(reports_data) + 6
        ws.cell(row=total_row, column=1, value='TOTALS').font = Font(bold=True)
        ws.cell(row=total_row, column=4, value=sum(r['bookings_count'] for r in reports_data)).font = Font(bold=True)
        ws.cell(row=total_row, column=5, value=sum(r['revenue'] for r in reports_data)).font = Font(bold=True)
        ws.cell(row=total_row, column=6, value=sum(r['passengers_count'] for r in reports_data)).font = Font(bold=True)
    
    # Adjust column widths
    column_widths = [12, 30, 15, 12, 15, 12]
    for i, width in enumerate(column_widths, 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = width
    
    # Prepare response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f"brts_report_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    wb.save(response)
    return response


def export_pdf_report(reports_data, start_date, end_date, report_type):
    """Export report to PDF format"""
    response = HttpResponse(content_type='application/pdf')
    filename = f"brts_report_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # Create PDF document
    doc = SimpleDocTemplate(response, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    story.append(Paragraph(f"BRTS Booking Report - {report_type.title() if report_type else 'Custom'}", title_style))
    
    # Date range
    date_style = ParagraphStyle(
        'CustomDate',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=20,
        alignment=1  # Center alignment
    )
    story.append(Paragraph(f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}", date_style))
    
    # Table data
    table_data = [['Date', 'Route', 'Bus', 'Bookings', 'Revenue (₹)', 'Passengers']]
    for report in reports_data:
        table_data.append([
            report['date'],
            report['route_name'],
            report['bus_number'],
            str(report['bookings_count']),
            f"₹{report['revenue']:.2f}",
            str(report['passengers_count'])
        ])
    
    # Add totals if data exists
    if reports_data:
        table_data.append([
            'TOTALS',
            '',
            '',
            str(sum(r['bookings_count'] for r in reports_data)),
            f"₹{sum(r['revenue'] for r in reports_data):.2f}",
            str(sum(r['passengers_count'] for r in reports_data))
        ])
    
    # Create table
    table = Table(table_data)
    
    # Style the table
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ]))
    
    # Make totals row bold
    if reports_data:
        table.setStyle(TableStyle([
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ]))
    
    story.append(table)
    story.append(Spacer(1, 12))
    
    # Build PDF
    doc.build(story)
    return response
