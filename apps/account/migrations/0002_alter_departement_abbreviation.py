# Generated by Django 4.2.10 on 2024-06-12 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='departement',
            name='abbreviation',
            field=models.CharField(blank=True, default='', max_length=10, verbose_name='Singkatan'),
        ),
    ]