# Generated by Django 4.2.10 on 2024-06-14 09:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0020_alter_assessmentreport_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assessmentreport',
            name='assessment_review',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assessment_report', to='proposals.assesmentreview'),
        ),
        migrations.AlterField(
            model_name='assessmentreport',
            name='stage_assessment_2',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assessment_report', to='proposals.stageassesment2'),
        ),
    ]
