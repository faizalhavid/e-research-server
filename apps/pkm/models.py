import hashlib
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from taggit.managers import TaggableManager
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import NON_FIELD_ERRORS
from utils.exceptions import ValidationError, failure_response_validation

class PKMProgram(models.Model):
    period = models.IntegerField()
    due_date = models.DateTimeField()
    scheme = models.ManyToManyField('pkm.PKMScheme', related_name='programs')
    
    class Meta:
        verbose_name = 'Program PKM'
        verbose_name_plural = 'Program PKM'

    def __str__(self):
        return f"PKM {self.period}"
    
class PKMActivitySchedule(models.Model):
    program = models.ForeignKey('pkm.PKMProgram', related_name='activity_schedules', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='')
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    
    class Meta:
        verbose_name = 'Jadwal Kegiatan PKM'
        verbose_name_plural = 'Jadwal Kegiatan PKM'
    def __str__(self):
        return f"{self.title} - {self.program}"

class PKMScheme(models.Model):
    name = models.CharField(max_length=50)
    abbreviation = models.CharField(max_length=10)
    description = models.TextField(blank=True, default='', max_length=255)
    
    class Meta:
        verbose_name = 'Schema PKM'
        verbose_name_plural = 'Schema PKM'
    def __str__(self):
        return self.name
    
class PKMIdeaContribute(models.Model):
    user = models.ForeignKey('account.User', on_delete=models.CASCADE, related_name='idea_contributes')
    title = models.CharField(max_length=100,unique=True)
    description = models.TextField(blank=True, default='')
    created = models.DateTimeField(auto_now_add=True)
    problem = ArrayField(models.TextField(), blank=True, default=list)
    solution = ArrayField(models.TextField(), blank=True, default=list)
    tags = TaggableManager()
    slug = models.SlugField( blank=True, null=True, max_length=255)
    image = models.ImageField(upload_to='pkm/idea_contribute/', blank=True, null=True)
    document = models.FileField(upload_to='pkm/idea_contribute/', blank=True, null=True)
    STATUS_CHOICES = (
        ('D', 'Draft'),
        ('P', 'Published'),
        ('A', 'Archived'),
        ('R', 'Rejected'),
    )
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='D')
    applied_date = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Bank Judul'
        verbose_name_plural = 'Bank Judul'
        ordering = ['-created']
        
    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = hashlib.sha256(self.title.encode('utf-8')).hexdigest()
        if self.status == 'P' and not self.applied_date:
            self.applied_date = timezone.now()
        super().save(*args, **kwargs)



class PKMIdeaContributeApplyTeam(models.Model):
    idea_contribute = models.ForeignKey('pkm.PKMIdeaContribute', on_delete=models.CASCADE, related_name='apply_teams')
    team = models.ForeignKey('team.Team', on_delete=models.CASCADE, related_name='apply_ideas')
    message = models.TextField(blank=True, default='')
    created = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = (
        ('P', 'Pending'),
        ('A', 'Accepted'),
        ('R', 'Rejected'),
    )
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    slug = models.SlugField(unique=True, blank=True, null=True)
    
    class Meta:
        verbose_name = 'Apply Team Idea Contribute'
        verbose_name_plural = 'Apply Team Idea Contribute'
        unique_together = ('idea_contribute', 'team')
    def __str__(self):
        
        return f"{self.team.name} - {self.idea_contribute.title}"
    



    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = hashlib.sha256((self.idea_contribute.title + self.team.name).encode('utf-8')).hexdigest()[:20]
        if self.status == 'A':
            # Set all other applications for the same idea_contribute to 'R'
            PKMIdeaContributeApplyTeam.objects.filter(
                idea_contribute=self.idea_contribute
            ).exclude(
                pk=self.pk
            ).update(status='R')
        super(PKMIdeaContributeApplyTeam, self).save(*args, **kwargs)
    
