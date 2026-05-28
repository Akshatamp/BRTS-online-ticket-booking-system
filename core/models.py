from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ContactMessage(models.Model):
    """Contact form messages"""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True, null=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"


class FAQ(models.Model):
    """Frequently Asked Questions"""
    question = models.CharField(max_length=300)
    answer = models.TextField()
    category = models.CharField(max_length=50, choices=[
        ('general', 'General'),
        ('booking', 'Booking'),
        ('payment', 'Payment'),
        ('cancellation', 'Cancellation'),
        ('technical', 'Technical'),
    ])
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"
        ordering = ['order', 'created_at']

    def __str__(self):
        return self.question


class Testimonial(models.Model):
    """User testimonials"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='testimonials')
    name = models.CharField(max_length=100)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    message = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Testimonial"
        verbose_name_plural = "Testimonials"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.rating} stars"


class News(models.Model):
    """News and announcements"""
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='news_images/', blank=True, null=True)
    is_published = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "News"
        verbose_name_plural = "News"
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Offer(models.Model):
    """Special offers and discounts"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    promo_code = models.CharField(max_length=20, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    min_booking_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    usage_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Offer"
        verbose_name_plural = "Offers"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.discount_percentage}%"

    def is_valid(self):
        """Check if offer is currently valid"""
        from django.utils import timezone
        today = timezone.now().date()
        return (self.is_active and 
                self.start_date <= today <= self.end_date and
                (self.usage_limit is None or self.usage_count < self.usage_limit))
