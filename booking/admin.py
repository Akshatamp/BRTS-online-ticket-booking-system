from django.contrib import admin
from .models import Booking, Payment, Ticket, Notification, Feedback


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_reference', 'user', 'passenger_name', 'route', 'bus', 'travel_date', 'booking_status', 'payment_status', 'total_fare')
    list_filter = ('booking_status', 'payment_status', 'travel_date', 'booking_date')
    search_fields = ('booking_reference', 'passenger_name', 'passenger_email', 'user__email')
    readonly_fields = ('id', 'booking_reference', 'created_at', 'updated_at')
    ordering = ['-booking_date']
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('booking_reference', 'user', 'schedule', 'bus', 'route', 'travel_date', 'booking_date')
        }),
        ('Passenger Details', {
            'fields': ('passenger_name', 'passenger_email', 'passenger_phone', 'passenger_age', 'passenger_gender')
        }),
        ('Booking Details', {
            'fields': ('seat_numbers', 'number_of_seats', 'total_fare', 'special_requests', 'notes')
        }),
        ('Status', {
            'fields': ('booking_status', 'payment_status')
        }),
        ('Cancellation', {
            'fields': ('cancellation_date', 'cancellation_reason', 'refund_amount'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['confirm_bookings', 'cancel_bookings']
    
    def confirm_bookings(self, request, queryset):
        queryset.update(booking_status='confirmed')
        self.message_user(request, 'Selected bookings have been confirmed.')
    confirm_bookings.short_description = 'Confirm selected bookings'
    
    def cancel_bookings(self, request, queryset):
        queryset.update(booking_status='cancelled')
        self.message_user(request, 'Selected bookings have been cancelled.')
    cancel_bookings.short_description = 'Cancel selected bookings'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'booking', 'amount', 'payment_method', 'payment_status', 'payment_date')
    list_filter = ('payment_method', 'payment_status', 'payment_date')
    search_fields = ('payment_id', 'booking__booking_reference', 'transaction_id')
    readonly_fields = ('id', 'payment_id', 'created_at', 'updated_at')
    ordering = ['-payment_date']
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('payment_id', 'booking', 'amount', 'payment_method', 'payment_status')
        }),
        ('Transaction Details', {
            'fields': ('transaction_id', 'gateway_response')
        }),
        ('Refund Details', {
            'fields': ('refund_id', 'refund_amount', 'refund_date'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('payment_date', 'completed_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_number', 'booking', 'is_valid', 'created_at')
    list_filter = ('is_valid', 'created_at', 'validated_at')
    search_fields = ('ticket_number', 'booking__booking_reference', 'booking__passenger_name')
    readonly_fields = ('id', 'ticket_number', 'created_at', 'updated_at')
    ordering = ['-created_at']
    
    actions = ['validate_tickets', 'invalidate_tickets']
    
    def validate_tickets(self, request, queryset):
        queryset.update(is_valid=True)
        self.message_user(request, 'Selected tickets have been validated.')
    validate_tickets.short_description = 'Validate selected tickets'
    
    def invalidate_tickets(self, request, queryset):
        queryset.update(is_valid=False)
        self.message_user(request, 'Selected tickets have been invalidated.')
    invalidate_tickets.short_description = 'Invalidate selected tickets'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'user__email', 'user__first_name')
    readonly_fields = ('created_at', 'read_at')
    ordering = ['-created_at']
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, 'Selected notifications marked as read.')
    mark_as_read.short_description = 'Mark selected notifications as read'
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
        self.message_user(request, 'Selected notifications marked as unread.')
    mark_as_unread.short_description = 'Mark selected notifications as unread'


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('subject', 'user', 'feedback_type', 'status', 'priority', 'created_at')
    list_filter = ('feedback_type', 'status', 'priority', 'created_at')
    search_fields = ('subject', 'message', 'user__email', 'user__first_name')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ['-created_at']
    
    fieldsets = (
        ('Feedback Information', {
            'fields': ('user', 'feedback_type', 'subject', 'message', 'priority')
        }),
        ('Related Objects', {
            'fields': ('booking',)
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Admin Response', {
            'fields': ('admin_response', 'responded_by', 'responded_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_resolved', 'mark_as_in_progress']
    
    def mark_as_resolved(self, request, queryset):
        queryset.update(status='resolved')
        self.message_user(request, 'Selected feedback marked as resolved.')
    mark_as_resolved.short_description = 'Mark selected feedback as resolved'
    
    def mark_as_in_progress(self, request, queryset):
        queryset.update(status='in_progress')
        self.message_user(request, 'Selected feedback marked as in progress.')
    mark_as_in_progress.short_description = 'Mark selected feedback as in progress'
