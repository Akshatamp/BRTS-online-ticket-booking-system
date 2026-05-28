# Generated migration to remove QR code field from Ticket model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ticket',
            name='qr_code',
        ),
    ]
