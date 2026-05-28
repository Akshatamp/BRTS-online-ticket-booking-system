from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Main pages
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('faq/', views.faq_view, name='faq'),
    
    # News
    path('news/', views.news_view, name='news'),
    path('news/<int:news_id>/', views.news_detail_view, name='news_detail'),
    
    # Offers
    path('offers/', views.offers_view, name='offers'),
    
    # Testimonials
    path('add-testimonial/', views.add_testimonial_view, name='add_testimonial'),
    
    # AJAX endpoints
    path('api/search-routes/', views.search_routes_json, name='search_routes_json'),
    path('api/route-info/<int:route_id>/', views.get_route_info_json, name='route_info_json'),
]
