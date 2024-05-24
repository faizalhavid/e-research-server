from django.db import models
from django.utils import timezone

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
    
