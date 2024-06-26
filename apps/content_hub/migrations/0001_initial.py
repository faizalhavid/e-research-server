# Generated by Django 4.2.13 on 2024-06-21 13:26

import ckeditor.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import utils.handle_file_upload


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('image', models.ImageField(blank=True, default='articles/default.jpg', null=True, upload_to='articles/')),
                ('excerpt', models.TextField(blank=True, null=True, verbose_name='kutipan')),
                ('status', models.CharField(choices=[('D', 'Draft'), ('P', 'Published'), ('A', 'Archived')], default='D', max_length=1)),
                ('likes', models.IntegerField(blank=True, default=0, null=True)),
                ('view', models.IntegerField(blank=True, default=0, null=True)),
                ('content', ckeditor.fields.RichTextField()),
                ('slug', models.SlugField(blank=True, max_length=100, null=True, unique=True)),
                ('author', models.ForeignKey(limit_choices_to={'is_staff': True}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Notice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('content', ckeditor.fields.RichTextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
                ('priority', models.CharField(choices=[('high', 'High'), ('medium', 'Medium'), ('low', 'Low')], default='medium', max_length=10)),
                ('attachment', models.FileField(blank=True, null=True, upload_to=utils.handle_file_upload.UploadToPathAndRename('notice/attachments/'))),
                ('slug', models.SlugField(blank=True, null=True, unique=True)),
                ('author', models.ForeignKey(limit_choices_to={'is_staff': True}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('content', models.TextField()),
                ('likes', models.IntegerField(default=0)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='content_hub.article')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
