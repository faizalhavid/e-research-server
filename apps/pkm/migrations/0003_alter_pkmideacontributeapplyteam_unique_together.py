# Generated by Django 4.2.13 on 2024-06-29 04:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0001_initial'),
        ('pkm', '0002_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='pkmideacontributeapplyteam',
            unique_together={('idea_contribute', 'team')},
        ),
    ]
