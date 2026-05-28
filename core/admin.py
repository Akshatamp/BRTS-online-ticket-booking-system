from django.contrib import admin
from .models import ContactMessage, FAQ, Testimonial, News, Offer


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at',)
    ordering = ['-created_at']
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, 'Selected messages marked as read.')
    mark_as_read.short_description = 'Mark selected messages as read'
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
        self.message_user(request, 'Selected messages marked as unread.')
    mark_as_unread.short_description = 'Mark selected messages as unread'


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'order', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('question', 'answer')
    list_editable = ('order', 'is_active')
    ordering = ['order', 'created_at']


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'rating', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_approved', 'created_at')
    search_fields = ('name', 'message')
    list_editable = ('is_approved',)
    ordering = ['-created_at']
    
    actions = ['approve_testimonials', 'disapprove_testimonials']
    
    def approve_testimonials(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, 'Selected testimonials approved.')
    approve_testimonials.short_description = 'Approve selected testimonials'
    
    def disapprove_testimonials(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, 'Selected testimonials disapproved.')
    disapprove_testimonials.short_description = 'Disapprove selected testimonials'


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'featured', 'created_at')
    list_filter = ('is_published', 'featured', 'created_at')
    search_fields = ('title', 'content')
    list_editable = ('is_published', 'featured')
    ordering = ['-created_at']
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('title', 'discount_percentage', 'promo_code', 'is_active', 'start_date', 'end_date')
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('title', 'promo_code', 'description')
    ordering = ['-created_at']
    readonly_fields = ('created_at', 'usage_count')
