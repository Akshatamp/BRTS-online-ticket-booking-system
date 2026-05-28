// BRTS Online Ticket Booking System - Custom JavaScript

// Dark Mode Toggle
document.addEventListener('DOMContentLoaded', function() {
    const darkModeToggle = document.getElementById('darkModeToggle');
    const body = document.body;
    
    // Check for saved dark mode preference
    const isDarkMode = localStorage.getItem('darkMode') === 'true';
    if (isDarkMode) {
        body.classList.add('dark-mode');
        updateDarkModeIcon(true);
    }
    
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function() {
            body.classList.toggle('dark-mode');
            const isDark = body.classList.contains('dark-mode');
            localStorage.setItem('darkMode', isDark);
            updateDarkModeIcon(isDark);
        });
    }
    
    function updateDarkModeIcon(isDark) {
        const icon = darkModeToggle.querySelector('i');
        if (isDark) {
            icon.classList.remove('fa-moon');
            icon.classList.add('fa-sun');
        } else {
            icon.classList.remove('fa-sun');
            icon.classList.add('fa-moon');
        }
    }
});

// Auto-complete for route search
function initializeRouteAutocomplete() {
    const sourceInput = document.getElementById('source');
    const destinationInput = document.getElementById('destination');
    
    if (sourceInput) {
        sourceInput.addEventListener('input', debounce(function(e) {
            fetchRoutes(e.target.value, 'source');
        }, 300));
    }
    
    if (destinationInput) {
        destinationInput.addEventListener('input', debounce(function(e) {
            fetchRoutes(e.target.value, 'destination');
        }, 300));
    }
}

function fetchRoutes(query, type) {
    if (query.length < 2) return;
    
    fetch(`/api/search-routes/?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            displayRouteSuggestions(data.routes, type);
        })
        .catch(error => {
            console.error('Error fetching routes:', error);
        });
}

function displayRouteSuggestions(routes, type) {
    // Implementation for displaying route suggestions
    console.log('Route suggestions:', routes, type);
}

// Debounce utility function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Form validation
function validateBookingForm() {
    const source = document.getElementById('source').value;
    const destination = document.getElementById('destination').value;
    const travelDate = document.getElementById('travelDate').value;
    
    let isValid = true;
    let errorMessage = '';
    
    if (!source.trim()) {
        isValid = false;
        errorMessage = 'Please enter source city';
    } else if (!destination.trim()) {
        isValid = false;
        errorMessage = 'Please enter destination';
    } else if (!travelDate) {
        isValid = false;
        errorMessage = 'Please select travel date';
    } else if (source.toLowerCase() === destination.toLowerCase()) {
        isValid = false;
        errorMessage = 'Source and destination cannot be the same';
    } else if (new Date(travelDate) < new Date().setHours(0,0,0,0)) {
        isValid = false;
        errorMessage = 'Travel date cannot be in the past';
    }
    
    if (!isValid) {
        showNotification(errorMessage, 'error');
    }
    
    return isValid;
}

// Notification system
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification-toast');
    existingNotifications.forEach(notification => notification.remove());
    
    // Create new notification
    const notification = document.createElement('div');
    notification.className = `notification-toast notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${getNotificationIcon(type)}"></i>
            <span>${message}</span>
            <button class="notification-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
    
    // Animate in
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
}

function getNotificationIcon(type) {
    const icons = {
        'success': 'check-circle',
        'error': 'exclamation-circle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Seat selection utilities
function initializeSeatSelection() {
    const seatButtons = document.querySelectorAll('.seat-btn');
    const selectedSeats = [];
    
    seatButtons.forEach(button => {
        button.addEventListener('click', function() {
            if (this.classList.contains('seat-booked')) return;
            
            const seatNumber = this.dataset.seat;
            
            if (this.classList.contains('seat-selected')) {
                this.classList.remove('seat-selected', 'bg-warning');
                this.classList.add('seat-available', 'btn-outline-success');
                selectedSeats.splice(selectedSeats.indexOf(seatNumber), 1);
            } else {
                this.classList.remove('seat-available', 'btn-outline-success');
                this.classList.add('seat-selected', 'bg-warning');
                selectedSeats.push(seatNumber);
            }
            
            updateSeatDisplay(selectedSeats);
            updateTotalPrice(selectedSeats);
        });
    });
}

function updateSeatDisplay(selectedSeats) {
    const display = document.getElementById('selectedSeatsDisplay');
    const list = document.getElementById('selectedSeatsList');
    
    if (selectedSeats.length === 0) {
        if (display) display.innerHTML = '<span class="text-muted">No seats selected</span>';
        if (list) list.innerHTML = '<span class="text-muted">No seats selected</span>';
    } else {
        const seatsText = selectedSeats.sort().join(', ');
        const badgesHtml = selectedSeats.map(seat => 
            `<span class="badge bg-warning">${seat}</span>`
        ).join(' ');
        
        if (display) display.innerHTML = `<span class="badge bg-warning">${seatsText}</span>`;
        if (list) list.innerHTML = badgesHtml;
    }
}

function updateTotalPrice(selectedSeats) {
    const baseFare = parseFloat(document.querySelector('[data-base-fare]')?.dataset.baseFare || 0);
    const total = selectedSeats.length * baseFare;
    const totalElement = document.getElementById('totalFare');
    
    if (totalElement) {
        totalElement.textContent = `₹${total.toFixed(2)}`;
    }
}

// Payment processing
function processPayment() {
    const paymentMethod = document.querySelector('input[name="payment_method"]:checked')?.value;
    const termsAccepted = document.getElementById('terms')?.checked;
    
    if (!termsAccepted) {
        showNotification('Please accept terms and conditions', 'error');
        return;
    }
    
    // Validate based on payment method
    let isValid = true;
    let errorMessage = '';
    
    if (paymentMethod === 'credit_card' || paymentMethod === 'debit_card') {
        const cardNumber = document.getElementById('cardNumber')?.value;
        const cardHolder = document.getElementById('cardHolder')?.value;
        const expiryDate = document.getElementById('expiryDate')?.value;
        const cvv = document.getElementById('cvv')?.value;
        
        if (!cardNumber || !cardHolder || !expiryDate || !cvv) {
            isValid = false;
            errorMessage = 'Please fill in all card details';
        }
    } else if (paymentMethod === 'upi') {
        const upiId = document.getElementById('upiId')?.value;
        if (!upiId) {
            isValid = false;
            errorMessage = 'Please enter your UPI ID';
        }
    } else if (paymentMethod === 'net_banking') {
        const bankName = document.getElementById('bankName')?.value;
        if (!bankName) {
            isValid = false;
            errorMessage = 'Please select your bank';
        }
    }
    
    if (!isValid) {
        showNotification(errorMessage, 'error');
        return;
    }
    
    // Show loading modal
    const modal = new bootstrap.Modal(document.getElementById('loadingModal'));
    modal.show();
    
    // Simulate payment processing
    setTimeout(() => {
        fetch('/booking/process-payment/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                payment_method: paymentMethod
            })
        })
        .then(response => response.json())
        .then(data => {
            modal.hide();
            if (data.success) {
                window.location.href = data.redirect_url;
            } else {
                showNotification('Payment failed: ' + data.message, 'error');
            }
        })
        .catch(error => {
            modal.hide();
            showNotification('Payment failed. Please try again.', 'error');
        });
    }, 2000);
}

// Utility functions
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR'
    }).format(amount);
}

function formatDate(date) {
    return new Intl.DateTimeFormat('en-IN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    }).format(new Date(date));
}

function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePhone(phone) {
    const re = /^[+]?[\d\s-()]{10,15}$/;
    return re.test(phone);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize components
    initializeRouteAutocomplete();
    
    // Initialize seat selection if on bus details page
    if (document.querySelector('.seat-btn')) {
        initializeSeatSelection();
    }
    
    // Initialize form validation
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            if (!validateBookingForm()) {
                e.preventDefault();
            }
        });
    }
    
    // Initialize payment form
    const paymentForm = document.getElementById('paymentForm');
    if (paymentForm) {
        paymentForm.addEventListener('submit', function(e) {
            e.preventDefault();
            processPayment();
        });
    }
    
    // Add smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add print functionality
    const printBtn = document.querySelector('[onclick*="window.print()"]');
    if (printBtn) {
        printBtn.addEventListener('click', function() {
            window.print();
        });
    }
});

// Export functions for global use
window.BRTS = {
    showNotification,
    validateEmail,
    validatePhone,
    formatCurrency,
    formatDate
};
