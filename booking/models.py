from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile

User = get_user_model()


class Booking(models.Model):
    """Ticket booking information"""
    BOOKING_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('expired', 'Expired'),
    ]

    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking_reference = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    schedule = models.ForeignKey('bus_management.Schedule', on_delete=models.CASCADE, related_name='bookings')
    bus = models.ForeignKey('bus_management.Bus', on_delete=models.CASCADE, related_name='bookings')
    route = models.ForeignKey('bus_management.Route', on_delete=models.CASCADE, related_name='bookings')
    
    # Passenger details
    passenger_name = models.CharField(max_length=100)
    passenger_email = models.EmailField()
    passenger_phone = models.CharField(max_length=15)
    passenger_age = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(120)]
    )
    passenger_gender = models.CharField(max_length=10, choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ])
    
    # Booking details
    seat_numbers = models.JSONField(help_text="List of seat numbers")
    number_of_seats = models.PositiveIntegerField(default=1)
    total_fare = models.DecimalField(max_digits=10, decimal_places=2)
    booking_date = models.DateTimeField(auto_now_add=True)
    travel_date = models.DateField()
    
    # Status
    booking_status = models.CharField(max_length=20, choices=BOOKING_STATUS, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    
    # Additional information
    special_requests = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    # Cancellation details
    cancellation_date = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True, null=True)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"
        ordering = ['-booking_date']

    def __str__(self):
        return f"Booking {self.booking_reference} - {self.passenger_name}"

    def save(self, *args, **kwargs):
        if not self.booking_reference:
            # Generate unique booking reference
            last_booking = Booking.objects.all().order_by('id').last()
            if last_booking:
                last_id = int(last_booking.booking_reference[3:])
            else:
                last_id = 0
            self.booking_reference = f"BRT{last_id + 1:06d}"
        
        if not self.number_of_seats:
            self.number_of_seats = len(self.seat_numbers) if self.seat_numbers else 1
            
        super().save(*args, **kwargs)

    def generate_qr_code(self):
        """Generate QR code for the booking"""
        qr_data = f"Booking ID: {self.id}\nReference: {self.booking_reference}\nPassenger: {self.passenger_name}\nBus: {self.bus.bus_number}\nRoute: {self.route.source} to {self.route.destination}\nDate: {self.travel_date}\nSeats: {', '.join(self.seat_numbers)}"
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save QR code to a file
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Save to booking
        filename = f"qr_{self.booking_reference}.png"
        self.qr_code.save(filename, ContentFile(buffer.read()), save=False)
        return filename

    def is_cancellable(self):
        """Check if booking can be cancelled"""
        if self.booking_status in ['cancelled', 'completed', 'expired']:
            return False
        
        # Check if travel date is in the future
        if self.travel_date <= timezone.now().date():
            return False
            
        # Check if booking is within cancellation window (e.g., 2 hours before departure)
        from datetime import datetime, timedelta
        travel_datetime = datetime.combine(self.travel_date, self.schedule.departure_time)
        if travel_datetime - timezone.now() < timedelta(hours=2):
            return False
            
        return True

    def calculate_refund_amount(self):
        """Calculate refund amount based on cancellation policy"""
        if not self.is_cancellable():
            return 0
        
        from datetime import datetime, timedelta
        travel_datetime = datetime.combine(self.travel_date, self.schedule.departure_time)
        time_until_travel = travel_datetime - timezone.now()
        
        if time_until_travel >= timedelta(days=2):
            return self.total_fare * 0.9  # 90% refund
        elif time_until_travel >= timedelta(hours=24):
            return self.total_fare * 0.7  # 70% refund
        elif time_until_travel >= timedelta(hours=2):
            return self.total_fare * 0.5  # 50% refund
        else:
            return 0  # No refund


class Payment(models.Model):
    """Payment information for bookings"""
    PAYMENT_METHODS = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('net_banking', 'Net Banking'),
        ('upi', 'UPI'),
        ('wallet', 'Digital Wallet'),
        ('cash', 'Cash'),
    ]

    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    payment_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    
    # Transaction details
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    gateway_response = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    payment_date = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Refund details
    refund_id = models.CharField(max_length=100, blank=True, null=True)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    refund_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        ordering = ['-payment_date']

    def __str__(self):
        return f"Payment {self.payment_id} - {self.booking.booking_reference}"

    def save(self, *args, **kwargs):
        if not self.payment_id:
            # Generate unique payment ID
            import random
            import string
            timestamp = str(int(timezone.now().timestamp()))
            random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            self.payment_id = f"PAY{timestamp}{random_str}"
        
        super().save(*args, **kwargs)


class Ticket(models.Model):
    """Generated tickets for confirmed bookings"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='ticket')
    ticket_number = models.CharField(max_length=20, unique=True)
    qr_code = models.ImageField(upload_to='ticket_qr_codes/', blank=True, null=True)
    pdf_file = models.FileField(upload_to='ticket_pdfs/', blank=True, null=True)
    
    # Ticket validation
    is_valid = models.BooleanField(default=True)
    validated_at = models.DateTimeField(null=True, blank=True)
    validated_by = models.CharField(max_length=100, blank=True, null=True)
    
    # Boarding information
    boarding_point = models.CharField(max_length=100, blank=True, null=True)
    reporting_time = models.TimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"
        ordering = ['-created_at']

    def __str__(self):
        return f"Ticket {self.ticket_number} - {self.booking.passenger_name}"

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            # Generate unique ticket number
            import uuid
            self.ticket_number = f"TKT{uuid.uuid4().hex[:8].upper()}"
        
        super().save(*args, **kwargs)

    def generate_qr_code(self):
        """Generate QR code for the ticket"""
        # Create simple text data for ticket information
        qr_data = f"""BRTS Bus Ticket
================
Ticket Number: {self.ticket_number}
Booking Reference: {self.booking.booking_reference}
Passenger: {self.booking.passenger_name}
Route: {self.booking.route.source} to {self.booking.route.destination}
Bus: {self.booking.bus.bus_number}
Date: {self.booking.travel_date.strftime("%d-%m-%Y")}
Departure: {self.booking.schedule.departure_time}
Seats: {', '.join(self.booking.seat_numbers)}
Fare: ₹{self.booking.total_fare}
Status: {self.booking.booking_status.title()}
================
BRTS Online Ticket Booking System"""
        
        qr = qrcode.QRCode(
            version=2,  # Increased version to handle more data
            error_correction=qrcode.constants.ERROR_CORRECT_M,  # Better error correction
            box_size=6,  # Reduced box size to make it less dense
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        filename = f"ticket_{self.ticket_number}.png"
        self.qr_code.save(filename, ContentFile(buffer.read()))
        self.save()  # Save the model to update the qr_code field
        return filename

    

class Notification(models.Model):
    """User notifications"""
    NOTIFICATION_TYPES = [
        ('booking', 'Booking'),
        ('payment', 'Payment'),
        ('cancellation', 'Cancellation'),
        ('reminder', 'Reminder'),
        ('promotion', 'Promotion'),
        ('system', 'System'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    
    # Related objects (optional)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    
    # Status
    is_read = models.BooleanField(default=False)
    is_email_sent = models.BooleanField(default=False)
    is_sms_sent = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.get_full_name()}"

    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.read_at = timezone.now()
        self.save()


class Feedback(models.Model):
    """User feedback and complaints"""
    FEEDBACK_TYPES = [
        ('complaint', 'Complaint'),
        ('suggestion', 'Suggestion'),
        ('compliment', 'Compliment'),
        ('query', 'Query'),
    ]

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedback')
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    
    # Related objects (optional)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, null=True, blank=True, related_name='feedback')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    priority = models.CharField(max_length=10, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ], default='medium')
    
    # Admin response
    admin_response = models.TextField(blank=True, null=True)
    responded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='responded_feedback')
    responded_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Feedback"
        verbose_name_plural = "Feedback"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.feedback_type} - {self.subject}"
