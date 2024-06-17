# Generated by Django 4.2.10 on 2024-06-17 06:49

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pkm', '0005_alter_pkmideacontribute_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pkmideacontribute',
            name='problem',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), blank=True, default=list, size=None),
        ),
        migrations.AlterField(
            model_name='pkmideacontribute',
            name='solution',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), blank=True, default=list, size=None),
        ),
    ]
