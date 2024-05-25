from django.db import models
from django.core.exceptions import ValidationError

from apps.account.models import Student

def team_directory_path(instance, filename):
    return f'team/{instance.name}/{filename}'


class Team(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    image = models.ImageField(upload_to=team_directory_path, blank=True, null=True)
    leader = models.ForeignKey('account.Student', related_name='led_teams', on_delete=models.CASCADE, blank=True, null=True)
    lecturer = models.ForeignKey('account.Lecturer', related_name='lectured_teams', on_delete=models.CASCADE, blank=True, null=True)
    members = models.ManyToManyField('account.Student', related_name='teams', blank=True)
    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('NOT_ACTIVE', 'Not Active'),
        ('COMPLETED', 'Completed'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name 
    



class TeamVacancies(models.Model):
    team = models.ForeignKey(Team, related_name='vacancies', on_delete=models.CASCADE)
    description = models.TextField()
    role = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField()
    
    
    def __str__(self):
        return self.team.name + ' - ' + self.name

    
class TeamApply(models.Model):
    vacanicies = models.ForeignKey(TeamVacancies, related_name='applies', on_delete=models.CASCADE)
    user = models.ForeignKey('account.User', related_name='applies', on_delete=models.CASCADE)
    STATUS = (
        ('APPLIED', 'Applied'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
    )
    status = models.CharField(max_length=10, choices=STATUS, default='APPLIED')
    created_at = models.DateTimeField(auto_now_add=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)

    def __str__(self):
        return self.vacanicies.name + ' - ' + self.user.firstname
    
class TeamTask(models.Model):
    team = models.ForeignKey(Team, related_name='agendas', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    due_time = models.DateTimeField()
    completed = models.BooleanField(default=False)
    def __str__(self):
        return self.team.name + ' - ' + self.title