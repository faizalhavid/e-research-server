# Generated by Django 4.2.13 on 2024-10-10 07:55

from django.db import migrations, models
from django.conf import settings

class Migration(migrations.Migration):

    dependencies = [
        ('team', '0001_initial'),
    ]

    operations = []

    if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql':
        operations.append(
            migrations.AlterField(
                model_name='teamvacancies',
                name='requirements',
                field=models.JSONField(blank=True, default=list),
            )
        )
    else:
        operations.append(
            migrations.AlterField(
                model_name='teamvacancies',
                name='requirements',
                field=models.TextField(blank=True, default=''),
            )
        )