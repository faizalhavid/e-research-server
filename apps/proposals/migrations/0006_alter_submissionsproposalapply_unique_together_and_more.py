# Generated by Django 4.2.10 on 2024-05-31 05:38

from django.db import migrations, models
import taggit.managers
import utils.handle_file_upload


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0002_rename_teamvacanicies_teamvacancies'),
        ('taggit', '0006_rename_taggeditem_content_type_object_id_taggit_tagg_content_8fc721_idx'),
        ('proposals', '0005_alter_assesmentsubmissionsproposal_options_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='submissionsproposalapply',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='submissionsproposalapply',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='submissionsproposalapply',
            name='proposal',
            field=models.FileField(blank=True, null=True, upload_to=utils.handle_file_upload.UploadToPathAndRename('proposals\\submission_proposal/apply')),
        ),
        migrations.AddField(
            model_name='submissionsproposalapply',
            name='slug',
            field=models.SlugField(blank=True, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='submissionsproposalapply',
            name='tags',
            field=taggit.managers.TaggableManager(blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='submissionsproposalapply',
            name='title',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='submissionsproposalapply',
            unique_together={('team', 'submission', 'title')},
        ),
        migrations.DeleteModel(
            name='Proposal',
        ),
    ]
