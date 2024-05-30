# Generated by Django 4.2.10 on 2024-05-30 05:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pkm', '0005_alter_pkmideacontribute_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pkmideacontribute',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='idea_contributes', to=settings.AUTH_USER_MODEL),
        ),
    ]
