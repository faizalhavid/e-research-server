# Generated by Django 4.2.10 on 2024-06-08 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pkm', '0011_remove_taggedwhatever_content_type_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='pkmideacontributeapplyteam',
            name='slug',
            field=models.SlugField(blank=True, null=True, unique=True),
        ),
    ]