# Generated by Django 4.2.10 on 2024-05-23 10:14

from django.db import migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0006_rename_taggeditem_content_type_object_id_taggit_tagg_content_8fc721_idx'),
        ('proposals', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposal',
            name='tag',
            field=taggit.managers.TaggableManager(blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
    ]
