from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST

from .models import ContactMessage, FAQ, Testimonial, News, Offer
from bus_management.models import Route, Bus, Schedule
from booking.models import Booking
from accounts.models import User


def home_view(request):
    """Home page view"""
    # Redirect admin users to bus management dashboard
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('bus_management:admin_dashboard')
    
    # Get featured routes
    popular_routes = Route.objects.filter(is_active=True).annotate(
        booking_count=Count('bookings')
    ).order_by('-booking_count')[:6]
    
    # Get testimonials
    testimonials = Testimonial.objects.filter(is_approved=True).order_by('-created_at')[:3]
    
    # Get latest news
    latest_news = News.objects.filter(is_published=True).order_by('-created_at')[:3]
    
    # Get active offers
    active_offers = Offer.objects.filter(is_active=True).order_by('-created_at')[:3]
    
    # Get statistics
    total_routes = Route.objects.filter(is_active=True).count()
    total_buses = Bus.objects.filter(status='active').count()
    total_bookings = Booking.objects.filter(booking_status='confirmed').count()
    total_users = User.objects.filter(is_active=True).count()
    
    context = {
        'popular_routes': popular_routes,
        'testimonials': testimonials,
        'latest_news': latest_news,
        'active_offers': active_offers,
        'total_routes': total_routes,
        'total_buses': total_buses,
        'total_bookings': total_bookings,
        'total_users': total_users,
    }
    return render(request, 'core/home.html', context)


def about_view(request):
    """About page view"""
    # Get statistics for about page
    total_routes = Route.objects.filter(is_active=True).count()
    total_buses = Bus.objects.filter(status='active').count()
    total_bookings = Booking.objects.filter(booking_status='confirmed').count()
    total_users = User.objects.filter(is_active=True).count()
    
    # Get featured testimonials
    featured_testimonials = Testimonial.objects.filter(is_approved=True).order_by('-created_at')[:6]
    
    context = {
        'total_routes': total_routes,
        'total_buses': total_buses,
        'total_bookings': total_bookings,
        'total_users': total_users,
        'featured_testimonials': featured_testimonials,
    }
    return render(request, 'core/about.html', context)


def contact_view(request):
    """Contact page view"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        if name and email and subject and message:
            ContactMessage.objects.create(
                name=name,
                email=email,
                phone=phone,
                subject=subject,
                message=message
            )
            messages.success(request, 'Your message has been sent successfully! We will get back to you soon.')
            return redirect('core:contact')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    return render(request, 'core/contact.html')


def faq_view(request):
    """FAQ page view"""
    faqs = FAQ.objects.filter(is_active=True).order_by('order', 'created_at')
    
    # Group FAQs by category
    categories = {}
    for faq in faqs:
        if faq.category not in categories:
            categories[faq.category] = []
        categories[faq.category].append(faq)
    
    return render(request, 'core/faq.html', {'categories': categories})


def news_view(request):
    """News page view"""
    news_list = News.objects.filter(is_published=True).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(news_list, 6)
    page_number = request.GET.get('page')
    news = paginator.get_page(page_number)
    
    return render(request, 'core/news.html', {'news': news})


def news_detail_view(request, news_id):
    """News detail view"""
    news = get_object_or_404(News, id=news_id, is_published=True)
    
    # Get related news
    related_news = News.objects.filter(
        is_published=True
    ).exclude(id=news_id).order_by('-created_at')[:3]
    
    return render(request, 'core/news_detail.html', {
        'news': news,
        'related_news': related_news
    })


def offers_view(request):
    """Offers page view"""
    offers = [
        {
            'title': 'Weekend Special',
            'description': 'Get 20% off on all weekend trips',
            'discount': '20',
            'validity': 'Valid on Saturday and Sunday',
            'conditions': 'Minimum booking amount ₹500',
            'original_price': '1000',
            'discounted_price': '800'
        },
        {
            'title': 'Early Bird Discount',
            'description': 'Book 7 days in advance and save 15%',
            'discount': '15',
            'validity': 'Valid for all routes',
            'conditions': 'Book 7 days before travel date',
            'original_price': '1500',
            'discounted_price': '1275'
        }
    ]
    return render(request, 'core/offers.html', {'offers': offers})


@login_required
def add_testimonial_view(request):
    """Add testimonial view"""
    if request.method == 'POST':
        rating = request.POST.get('rating')
        message = request.POST.get('message')
        
        if rating and message:
            Testimonial.objects.create(
                user=request.user,
                name=request.user.get_full_name(),
                rating=int(rating),
                message=message
            )
            messages.success(request, 'Thank you for your feedback! Your testimonial will be reviewed and published soon.')
            return redirect('core:home')
        else:
            messages.error(request, 'Please provide both rating and message.')
    
    return render(request, 'core/add_testimonial.html')


def search_routes_json(request):
    """AJAX endpoint for route search"""
    query = request.GET.get('q', '')
    
    if len(query) >= 2:
        routes = Route.objects.filter(
            Q(source__icontains=query) | Q(destination__icontains=query),
            is_active=True
        ).values('id', 'source', 'destination')[:10]
        
        return JsonResponse({'routes': list(routes)})
    
    return JsonResponse({'routes': []})


def get_route_info_json(request, route_id):
    """AJAX endpoint for route information"""
    try:
        route = Route.objects.get(id=route_id, is_active=True)
        
        # Get available schedules for this route
        schedules = Schedule.objects.filter(
            route=route,
            is_active=True
        ).select_related('bus').order_by('departure_time')
        
        schedule_data = []
        for schedule in schedules:
            schedule_data.append({
                'id': schedule.id,
                'bus_number': schedule.bus.bus_number,
                'bus_type': schedule.bus.bus_type,
                'departure_time': schedule.departure_time.strftime('%H:%M'),
                'arrival_time': schedule.arrival_time.strftime('%H:%M'),
                'available_seats': schedule.get_available_seats_count(),
                'fare': float(route.base_fare),
            })
        
        route_data = {
            'id': route.id,
            'source': route.source,
            'destination': route.destination,
            'distance': route.distance,
            'estimated_time': route.estimated_time,
            'base_fare': float(route.base_fare),
            'stops': route.stops,
            'schedules': schedule_data,
        }
        
        return JsonResponse(route_data)
    
    except Route.DoesNotExist:
        return JsonResponse({'error': 'Route not found'}, status=404)
