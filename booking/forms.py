from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from datetime import date


class BookingForm(forms.Form):
    """Booking search form"""
    source = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter source city',
            'autocomplete': 'off'
        })
    )
    destination = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter destination',
            'autocomplete': 'off'
        })
    )
    travel_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    def clean_travel_date(self):
        travel_date = self.cleaned_data['travel_date']
        if travel_date < date.today():
            raise ValidationError("Travel date cannot be in the past.")
        return travel_date
    
    def clean(self):
        cleaned_data = super().clean()
        source = cleaned_data.get('source')
        destination = cleaned_data.get('destination')
        
        if source and destination and source.lower() == destination.lower():
            raise ValidationError("Source and destination cannot be the same.")
        
        return cleaned_data


class PassengerDetailsForm(forms.Form):
    """Passenger details form"""
    passenger_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter passenger name'
        })
    )
    passenger_email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email address'
        })
    )
    passenger_phone = forms.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter phone number'
        })
    )
    passenger_age = forms.IntegerField(
        min_value=1,
        max_value=120,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter age'
        })
    )
    passenger_gender = forms.ChoiceField(
        choices=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    special_requests = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Any special requests (optional)'
        })
    )


class PaymentForm(forms.Form):
    """Payment form"""
    PAYMENT_METHODS = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('net_banking', 'Net Banking'),
        ('upi', 'UPI'),
        ('wallet', 'Digital Wallet'),
    ]
    
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHODS,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        })
    )
    
    # Credit/Debit Card fields
    card_number = forms.CharField(
        required=False,
        max_length=19,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '1234 5678 9012 3456',
            'id': 'cardNumber'
        })
    )
    card_holder = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Card Holder Name'
        })
    )
    expiry_date = forms.CharField(
        required=False,
        max_length=5,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'MM/YY',
            'id': 'expiryDate'
        })
    )
    cvv = forms.CharField(
        required=False,
        max_length=4,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'CVV',
            'id': 'cvv'
        })
    )
    
    # UPI field
    upi_id = forms.CharField(
        required=False,
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'your-upi-id@paytm'
        })
    )
    
    # Net Banking field
    bank_name = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Select Bank'),
            ('sbi', 'State Bank of India'),
            ('hdfc', 'HDFC Bank'),
            ('icici', 'ICICI Bank'),
            ('axis', 'Axis Bank'),
            ('pnb', 'Punjab National Bank'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        
        if payment_method in ['credit_card', 'debit_card']:
            card_number = cleaned_data.get('card_number')
            card_holder = cleaned_data.get('card_holder')
            expiry_date = cleaned_data.get('expiry_date')
            cvv = cleaned_data.get('cvv')
            
            if not all([card_number, card_holder, expiry_date, cvv]):
                raise ValidationError("All card details are required for card payments.")
        
        elif payment_method == 'upi':
            upi_id = cleaned_data.get('upi_id')
            if not upi_id:
                raise ValidationError("UPI ID is required for UPI payments.")
        
        elif payment_method == 'net_banking':
            bank_name = cleaned_data.get('bank_name')
            if not bank_name:
                raise ValidationError("Please select a bank for net banking.")
        
        return cleaned_data


class CancellationForm(forms.Form):
    """Booking cancellation form"""
    reason = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Please provide a reason for cancellation (optional)'
        })
    )
