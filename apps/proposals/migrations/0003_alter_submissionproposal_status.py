# Generated by Django 4.2.13 on 2024-06-27 08:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submissionproposal',
            name='status',
            field=models.CharField(choices=[('ARCHIVED', 'Archived'), ('PUBLISHED', 'Published'), ('CLOSED', 'Closed')], default='SUBMITTED', max_length=10),
        ),
    ]
