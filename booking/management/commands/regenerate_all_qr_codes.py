from django.core.management.base import BaseCommand
from booking.models import Ticket


class Command(BaseCommand):
    help = 'Regenerate QR codes for all tickets with new URL format'

    def handle(self, *args, **options):
        tickets = Ticket.objects.all()
        
        count = tickets.count()
        
        if count == 0:
            self.stdout.write(self.style.WARNING('No tickets found.'))
            return
        
        self.stdout.write(f'Found {count} tickets. Regenerating QR codes...')
        
        for ticket in tickets:
            try:
                # Clear existing QR code
                if ticket.qr_code:
                    ticket.qr_code.delete(save=False)
                
                # Generate new QR code
                ticket.generate_qr_code()
                self.stdout.write(self.style.SUCCESS(f'Regenerated QR code for ticket {ticket.ticket_number}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error regenerating QR code for ticket {ticket.ticket_number}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS('QR code regeneration completed.'))
