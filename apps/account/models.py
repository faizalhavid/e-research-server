import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import Group
from utils.handle_file_upload import UploadToPathAndRename
from utils.handle_image_upload import crop_image_to_square, handle_image_replacement



class UserManager(BaseUserManager):
    use_in_migrations = True
    
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Users require an email field')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
        
    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser',False)
        return self._create_user(email,password,**extra_fields)
    
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)
    
class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    objects = UserManager()
    username = models.CharField(max_length=50, unique=False, blank=True)
    string_activation = models.CharField(max_length=100, blank=True, default='')
    last_activity = models.DateTimeField(null=True, blank=True)
    USERNAME_FIELD = 'email'
    
    REQUIRED_FIELDS = []
    object = UserManager()
    
    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email.split('@')[0]
        super().save(*args, **kwargs) 
        if self.is_superuser:  # Don't change is_staff for superusers
            if self.groups.exists():
                if Group.objects.filter(name='Admin').exists() and Group.objects.get(name='Admin') in self.groups.all() or Group.objects.filter(name='LecturerReview').exists() and Group.objects.get(name='LecturerReview') in self.groups.all():
                    self.is_staff = True
                else:
                    self.is_staff = False
            else:
                self.is_staff = False
        super().save(*args, **kwargs)    
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True, related_name='user_profile')
    full_name = models.CharField(max_length=100, blank=True, default='')
    image = models.ImageField(upload_to=UploadToPathAndRename('accounts/profile_pictures/'),null=True, blank=True)
    address = models.CharField(max_length=100, blank=True, default='')
    phone_number = models.CharField(max_length=20, blank=True, default='')
    birth_date = models.DateField(null=True, blank=True)

    
    def __str__(self):
        return self.full_name
    
    def save(self, *args, **kwargs):
        handle_image_replacement(self)
        super().save(*args, **kwargs)
        crop_image_to_square(self)
    
class Departement(models.Model):
    name = models.CharField(max_length=50, blank=True, default='')
    abbreviation = models.CharField(max_length=10, blank=True, default='')
    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        conjunctions = ['and', 'or', 'but', 'nor', 'so', 'for', 'yet', 'after', 'although', 'as', 'because', 'before', 'even', 'if', 'once', 'since', 'though', 'unless', 'until', 'when', 'where', 'while', 'dan', 'atau', 'tetapi', 'ataupun', 'sehingga', 'agar', 'setelah', 'meskipun', 'karena', 'sebelum', 'jika', 'sampai', 'ketika', 'dimana', 'walaupun', 'kecuali', 'hingga']
        words = self.name.split()
        abbreviation = ''.join(word[0].upper() for word in words if word.lower() not in conjunctions)
        self.abbreviation = abbreviation
        super().save(*args, **kwargs)

class Major(models.Model):
    name = models.CharField(max_length=50, blank=True, default='')
    department = models.ForeignKey(Departement, related_name='majors', on_delete=models.CASCADE, null=True)
    def __str__(self):
        return self.name


class Student(UserProfile):
    nrp = models.CharField(max_length=18, unique=True)
    department = models.ForeignKey(Departement, related_name='students', on_delete=models.CASCADE, null=True)
    DEGREE_CHOICES = (
        ('d3', 'D3'),
        ('d4', 'D4'),
        ('d3 kampus-lamongan' , 'D3 Kampus-Lamongan'),
        ('d3 kampus-sumenep', 'D3 Kampus-Sumenep'),
        ('d4 lj', 'D4 LJ'),
        ('d3 pjj', 'D3 PJJ'),
    )
    degree = models.CharField(max_length=18, choices=DEGREE_CHOICES, default='d3')
    major = models.ForeignKey(Major, related_name='students', on_delete=models.SET_NULL, null=True, blank=True)
    admission_year = models.IntegerField(default=2020, null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.user is not None:
            student_group, created = Group.objects.get_or_create(name='Student')
            self.user.groups.add(student_group)

    def __str__(self):
        return self.full_name



class Lecturer(UserProfile):
    nidn = models.CharField(max_length=18, unique=True)
    department = models.ForeignKey(Departement, related_name='lecturers', on_delete=models.CASCADE, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.user : 
            lecturer_group, created = Group.objects.get_or_create(name='Lecturer')
            self.user.groups.add(lecturer_group)
            
    def __str__(self):
        return self.full_name
        
class Guest(UserProfile):
    agency = models.CharField(max_length=100, blank=True, null=True, default='')
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        guest_group, created = Group.objects.get_or_create(name='Guest')
        self.user.groups.add(guest_group)

    def __str__(self):
        return self.full_name




@receiver(m2m_changed, sender=User.groups.through)
def update_staff_status(sender, instance, action, **kwargs):
    if action in ['post_add', 'post_remove']:
        instance.is_staff = Group.objects.get(name='Admin') in instance.groups.all()
        instance.save()
    
@receiver(pre_delete, sender=User)
def delete_outstanding_tokens(sender, instance, **kwargs):
    try : 
        OutstandingToken.objects.filter(user=instance).delete()
    except:
        pass