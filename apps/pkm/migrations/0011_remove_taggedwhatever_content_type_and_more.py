# Generated by Django 4.2.10 on 2024-06-07 01:31

from django.db import migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0006_rename_taggeditem_content_type_object_id_taggit_tagg_content_8fc721_idx'),
        ('pkm', '0010_customtag_taggedwhatever_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='taggedwhatever',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='taggedwhatever',
            name='tag',
        ),
        migrations.AlterField(
            model_name='pkmideacontribute',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.DeleteModel(
            name='CustomTag',
        ),
        migrations.DeleteModel(
            name='TaggedWhatever',
        ),
    ]