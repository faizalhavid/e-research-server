import hashlib
from django.utils import timezone
from django.db import models
from ckeditor.fields import RichTextField
from django.utils.text import slugify
from apps.account.models import User
from apps.pkm.models import PKMIdeaContribute
from apps.proposals.models import SubmissionsProposalApply
from utils.exceptions import failure_response_validation
from utils.handle_file_upload import UploadToPathAndRename
from taggit.managers import TaggableManager
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
# Create your models here.
class Notice(models.Model):
    title = models.CharField(max_length=200)
    content = RichTextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_staff': True})
    created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    priority = models.CharField(
        max_length=10,
        choices=[
            ('high', 'High'),
            ('medium', 'Medium'),
            ('low', 'Low'),
        ],
        default='medium'
    )
    attachment = models.FileField(upload_to=UploadToPathAndRename('notice/attachments/'), blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True, null=True)

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = hashlib.sha256(self.title.encode()).hexdigest()[:15]
        super().save(*args, **kwargs)
    

class Article(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_staff': True})
    created = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='articles/', default='articles/default.jpg', blank=True, null=True)

    excerpt = models.TextField(blank=True, null=True,verbose_name='kutipan')
    STATUS_CHOICES = (
        ('D', 'Draft'),
        ('P', 'Published'),
        ('A', 'Archived')
    )
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='D')
    likes = models.IntegerField(default=0, blank=True, null=True)
    view = models.IntegerField(default=0, blank=True, null=True)
    content = RichTextField()
    slug = models.SlugField(unique=True, blank=True, null=True, max_length=100)
    tags = TaggableManager()
    
    idea_contribute = models.ForeignKey(PKMIdeaContribute, on_delete=models.CASCADE, blank=True, null=True, limit_choices_to={'status': 'P'})
    submission_proposal_apply = models.ForeignKey(
        SubmissionsProposalApply,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        limit_choices_to={'status__in': ['PASSED', 'PASSED FUNDING']}
    )
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return f'/article/{self.slug}'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.excerpt:
            self.excerpt = self.content[:100]
        super().save(*args, **kwargs)

    

    
class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    author = models.ForeignKey('account.User', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    likes = models.IntegerField(default=0)

    def __str__(self):
        return self.content[:50]
