# Generated migration to add QR code field back to Ticket model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0003_remove_ticket_qr_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='qr_code',
            field=models.ImageField(blank=True, null=True, upload_to='ticket_qr_codes/'),
        ),
    ]
