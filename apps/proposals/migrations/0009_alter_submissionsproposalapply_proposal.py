# Generated by Django 4.2.10 on 2024-05-31 13:52

from django.db import migrations, models
import utils.handle_file_upload


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0008_alter_submissionsproposalapply_tags_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submissionsproposalapply',
            name='proposal',
            field=models.FileField(default='/default.pdf', upload_to=utils.handle_file_upload.UploadToPathAndRename('proposals\\submission_proposal/apply')),
            preserve_default=False,
        ),
    ]
