# Generated by Django 4.2.10 on 2024-06-14 07:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0017_assesmentreport'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssessmentReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assessment_review', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='assessment_report', to='proposals.assesmentreview')),
                ('assessment_submission_proposal', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='assessment_report', to='proposals.assesmentsubmissionsproposal')),
                ('stage_assessment_1', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='assessment_report', to='proposals.stageassesment1')),
                ('stage_assessment_2', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='assessment_report', to='proposals.stageassesment2')),
            ],
            options={
                'verbose_name': 'Assessment Report',
                'verbose_name_plural': 'Assessment Reports',
            },
        ),
        migrations.DeleteModel(
            name='AssesmentReport',
        ),
    ]