# Generated by Django 4.2.10 on 2024-06-13 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0012_remove_assesmentsubmissionsproposal_comment_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='assesmentreport',
            name='final_score',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=5),
            preserve_default=False,
        ),
    ]