# Generated by Django 4.2.10 on 2024-05-31 00:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0002_rename_teamvacanicies_teamvacancies'),
        ('pkm', '0008_remove_pkmideacontribute_attachment_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pkmideacontribute',
            name='team',
        ),
        migrations.CreateModel(
            name='PKMIdeaContributeApplyTeam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('P', 'Pending'), ('A', 'Accepted'), ('R', 'Rejected')], default='P', max_length=1)),
                ('idea_contribute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='apply_teams', to='pkm.pkmideacontribute')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='apply_ideas', to='team.team')),
            ],
            options={
                'verbose_name': 'Apply Team Idea Contribute',
                'verbose_name_plural': 'Apply Team Idea Contribute',
            },
        ),
    ]