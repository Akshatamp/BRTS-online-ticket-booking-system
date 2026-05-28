from django.core.management.base import BaseCommand
from booking.models import Ticket


class Command(BaseCommand):
    help = 'Generate QR codes for tickets that are missing them'

    def handle(self, *args, **options):
        tickets_without_qr = Ticket.objects.filter(qr_code__isnull=True) | Ticket.objects.filter(qr_code='')
        
        count = tickets_without_qr.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('All tickets have QR codes.'))
            return
        
        self.stdout.write(f'Found {count} tickets without QR codes. Generating...')
        
        for ticket in tickets_without_qr:
            try:
                ticket.generate_qr_code()
                self.stdout.write(self.style.SUCCESS(f'Generated QR code for ticket {ticket.ticket_number}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error generating QR code for ticket {ticket.ticket_number}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS('QR code generation completed.'))
