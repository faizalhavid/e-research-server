# Generated by Django 4.2.13 on 2024-06-23 08:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('content_hub', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='content_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='article',
            name='object_id',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
