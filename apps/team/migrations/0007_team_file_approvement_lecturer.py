# Generated by Django 4.2.10 on 2024-06-05 04:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0006_team_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='file_approvement_lecturer',
            field=models.FileField(blank=True, null=True, upload_to='team/approvement/'),
        ),
    ]
