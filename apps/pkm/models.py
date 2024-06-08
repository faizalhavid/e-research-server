import hashlib
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from taggit.managers import TaggableManager
from django.contrib.postgres.fields import ArrayField

class PKMProgram(models.Model):
    name = models.CharField(max_length=50, blank=True)
    period = models.IntegerField()
    due_date = models.DateTimeField()
    scheme = models.ManyToManyField('pkm.PKMScheme', related_name='programs')
    
    class Meta:
        verbose_name = 'Program PKM'
        verbose_name_plural = 'Program PKM'

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = f"PKM {self.period}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name 
    
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
        return f"{self.title} - {self.program.name}"

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
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='')
    created = models.DateTimeField(auto_now_add=True)
    problem = ArrayField(models.CharField(max_length=200), blank=True, default=list)
    solution = ArrayField(models.CharField(max_length=200), blank=True, default=list)
    tags = TaggableManager()
    slug = models.SlugField(unique=True, blank=True, null=True, max_length=255)
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
        verbose_name = 'Idea Contribute'
        verbose_name_plural = 'Idea Contribute'
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
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
    def __str__(self):
        if not self.slug:
            self.slug = hashlib.sha256(self.name.encode()).hexdigest()
        
        return f"{self.team.name} - {self.idea_contribute.title}"
    
    
    
