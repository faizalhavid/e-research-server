# Generated by Django 4.2.10 on 2024-06-12 00:36

from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('taggit', '0006_rename_taggeditem_content_type_object_id_taggit_tagg_content_8fc721_idx'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PKMScheme',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('abbreviation', models.CharField(max_length=10)),
                ('description', models.TextField(blank=True, default='', max_length=255)),
            ],
            options={
                'verbose_name': 'Schema PKM',
                'verbose_name_plural': 'Schema PKM',
            },
        ),
        migrations.CreateModel(
            name='PKMProgram',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('period', models.IntegerField(default=2024)),
                ('due_date', models.DateTimeField()),
                ('scheme', models.ManyToManyField(related_name='programs', to='pkm.pkmscheme')),
            ],
            options={
                'verbose_name': 'Program PKM',
                'verbose_name_plural': 'Program PKM',
            },
        ),
        migrations.CreateModel(
            name='PKMIdeaContribute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, default='')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('problem', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200), blank=True, default=list, size=None)),
                ('solution', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200), blank=True, default=list, size=None)),
                ('slug', models.SlugField(blank=True, max_length=255, null=True, unique=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='pkm/idea_contribute/')),
                ('document', models.FileField(blank=True, null=True, upload_to='pkm/idea_contribute/')),
                ('status', models.CharField(choices=[('D', 'Draft'), ('P', 'Published'), ('A', 'Archived'), ('R', 'Rejected')], default='D', max_length=1)),
                ('applied_date', models.DateTimeField(blank=True, null=True)),
                ('tags', taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='idea_contributes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Idea Contribute',
                'verbose_name_plural': 'Idea Contribute',
            },
        ),
        migrations.CreateModel(
            name='PKMActivitySchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, default='')),
                ('start_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('end_date', models.DateTimeField()),
                ('program', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activity_schedules', to='pkm.pkmprogram')),
            ],
            options={
                'verbose_name': 'Jadwal Kegiatan PKM',
                'verbose_name_plural': 'Jadwal Kegiatan PKM',
            },
        ),
    ]
