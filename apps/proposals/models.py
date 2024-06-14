import hashlib
from django.db import models
from django.db import models
from django.dispatch import receiver
from django.forms import ValidationError
from taggit.managers import TaggableManager
import os
from django.db.models.signals import m2m_changed

from utils.exceptions import failure_response_validation
from utils.handle_file_upload import UploadToPathAndRename
from django.db.models.signals import post_save




class SubmissionProposal(models.Model):
    program = models.ForeignKey('pkm.PKMProgram', related_name='submissions', on_delete=models.CASCADE, default=1)
    BATCH_CHOICES = [
        ('BATCH 1', 'Batch 1'),
        ('BATCH 2', 'Batch 2'),
        ('BATCH 3', 'Batch 3'),
        ('REVISION', 'Revision'),
    ]
    title = models.CharField(max_length=10, choices=BATCH_CHOICES, default='BATCH 1', verbose_name='Batch')
    description=models.TextField( blank=True, default='')
    created_at=models.DateTimeField(auto_now_add=True)
    due_time = models.DateTimeField()
    additional_file = models.FileField(upload_to=UploadToPathAndRename(os.path.join('proposals', 'submission_proposal/additional_file')), blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    STATUS = (
        ('ARCHIVED', 'Archived'),
        ('PUBLISHED', 'Published'),
    )
    status = models.CharField(max_length=10, choices=STATUS, default='SUBMITTED')

    class Meta:
        verbose_name_plural = 'Submission Proposals'
        

    def __str__(self):
        return f"{self.title} - {self.program.period}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.title.replace(' ', '-').lower()
        super().save(*args, **kwargs)
    
class SubmissionsProposalApply(models.Model):
    submission = models.ForeignKey('proposals.SubmissionProposal', related_name='applies', on_delete=models.CASCADE)
    category = models.ForeignKey('pkm.PKMScheme', related_name='submissions_proposals_apply', on_delete=models.CASCADE, blank=True, null=True)
    STATUS = (
        ('APPLIED', 'Applied'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('REVISION', 'Revision'),
        ('PASSED', 'Passed'),
        ('PASSED FUNDING', 'Passed Funding'),
    )
    status = models.CharField(max_length=15, choices=STATUS, default='APPLIED')
    submitted_at = models.DateTimeField(auto_now_add=True)
    team = models.ForeignKey('team.Team', related_name='submissions_proposals_apply', on_delete=models.CASCADE)
    lecturer = models.ForeignKey('account.Lecturer', related_name='submissions_proposals_apply', on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    tags = TaggableManager( related_name='submissions_proposals_apply')
    proposal = models.FileField(upload_to=UploadToPathAndRename(os.path.join('proposals', 'submission_proposal/apply')))
    slug = models.SlugField(unique=True, blank=True, null=True)
    def __str__(self):
        return f"{self.team.name} - {self.submission.title}"
    
    class Meta:
        verbose_name_plural = 'Proposal Mahasiswa'

    def save(self, *args, **kwargs):
        if not self.category:
            self.category = self.submission.program.scheme.first()  

        if not self.slug:
            self.slug = hashlib.sha256(self.title.encode()).hexdigest()[:15]
        super().save(*args, **kwargs)

# class Proposal(models.Model):
#     team = models.ForeignKey('team.Team', related_name='proposals', on_delete=models.CASCADE, null=True, blank=True)
#     title = models.CharField(max_length=200)
#     description = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     file = models.FileField(upload_to=UploadToPathAndRename(os.path.join('proposals', 'proposal/file')), blank=True, null=True)
#     tag = TaggableManager(blank=True, related_name='proposals')
#     class Meta:
#         verbose_name_plural = '5. Proposal Mahasiswa'

#     def __str__(self):
#         return f"{self.title} - {self.team.name}"
    


class KeyStageAssesment2(models.Model):
    title = models.CharField(max_length=100,unique=True)
    description = models.TextField(blank=True, default='')
    presentase = models.DecimalField(max_digits=5, decimal_places=2,verbose_name='Bobot')
    category = models.ManyToManyField('pkm.PKMScheme', related_name='key_assesments')
    
    class Meta:
        verbose_name = 'Parameter Penilaian Tahap 2'
        verbose_name_plural = 'Parameter Penilaian Tahap 2'
    
    def __str__(self):
        # Convert to integer if no decimal part, else keep as decimal
        percentage_value = int(self.presentase) if self.presentase == self.presentase.to_integral() else self.presentase
        return f"{self.title} - {percentage_value}%"
    
class KeyStageAssesment1(models.Model):
    title = models.TextField(max_length=180)
    description = models.TextField(blank=True, default='')
    
    class Meta:
        verbose_name = 'Parameter Penilaian Tahap 1'
        verbose_name_plural = 'Parameter Penilaian Tahap 1'
    
    def __str__(self):
        return self.title

class LecturerTeamSubmissionApply(models.Model):
    lecturer = models.ForeignKey('account.Lecturer', related_name='team_submission_apply', on_delete=models.CASCADE)
    submission_apply = models.ManyToManyField(SubmissionsProposalApply, related_name='lecturers')
    
    class Meta:
        
        verbose_name = 'Pembagian Team & Reviewer'
        
            
class AssesmentSubmissionsProposal(models.Model):
    submission_apply = models.ForeignKey('proposals.SubmissionsProposalApply', related_name='assesments', on_delete=models.CASCADE)
    reviewer = models.ForeignKey('account.Lecturer', related_name='assesments', on_delete=models.CASCADE)
    reviewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('submission_apply', 'reviewer',)
        verbose_name_plural = 'Penilaian Proposal'

    def __str__(self):
        return f"{self.submission_apply.team.name} - Reviewed by : {self.reviewer.full_name}"

    def clean(self):
        if not (self.reviewer.user.groups.filter(name='Lecturer').exists() and self.reviewer.user.groups.filter(name='LecturerReviewer').exists()):
            raise ValidationError('Reviewer must be in the Lecturer and LecturerReviewer groups.')


        super().clean()
class StageAssesment1(models.Model):
    key_assesment = models.ForeignKey(KeyStageAssesment1, related_name='assessment_values_1', on_delete=models.CASCADE)
    assesment = models.ForeignKey(AssesmentSubmissionsProposal, related_name='assessment_values_1', on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    

    class Meta:
        unique_together = ('key_assesment', 'assesment',)
        verbose_name = 'Penilaian Tahap 1'
        verbose_name_plural = 'Penilaian Tahap 1'
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  
        self.assesment.refresh_from_db()
        if any(sa.status for sa in self.assesment.assessment_values_1.all()):
            self.assesment.submission_apply.status = SubmissionsProposalApply.STATUS[3][0]
        self.assesment.submission_apply.save()


    def __str__(self):
        return f"{self.key_assesment.title} - {self.assesment.submission_apply.team.name}"
class StageAssesment2(models.Model):
    key_assesment = models.ForeignKey(KeyStageAssesment2, related_name='assessment_values_2', on_delete=models.CASCADE)
    assesment = models.ForeignKey(AssesmentSubmissionsProposal, related_name='assessment_values_2', on_delete=models.CASCADE)

    SCORE_CHOICES = [
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (5, '5'),
    (6, '6'),
    (7, '7'),
    ]
    score = models.IntegerField(choices=SCORE_CHOICES)
    

    def create(self, *args, **kwargs):
        scores = [sa.score for sa in self.assesment.assessment_values_2.all()]
        
        if any(score < 1 for score in scores):
            self.assesment.submission_apply.status = SubmissionsProposalApply.STATUS[3][0]
        elif any(score < 5 for score in scores):
            self.assesment.submission_apply.status = SubmissionsProposalApply.STATUS[4][0]
        
        self.assesment.submission_apply.save()
    class Meta:
        unique_together = ('key_assesment', 'assesment',)
        verbose_name = 'Penilaian Tahap 2'
        verbose_name_plural = 'Penilaian Tahap 2'

    def __str__(self):
        return f"{self.assesment.submission_apply.submission.title} - {self.key_assesment.title}: {self.score}"
class AssesmentReport(models.Model):
    assesment = models.ForeignKey(AssesmentSubmissionsProposal, related_name='assesment_report', on_delete=models.CASCADE)
    comment = models.TextField(blank=True, default='')
    REVISION_CHOICES = [
    ('Revision Minor', 'Revision Minor'),
    ('Revision Major', 'Revision Major'),
    ('No Revision', 'No Revision'),
    ]
    final_score = models.DecimalField(max_digits=5, decimal_places=2,blank=True, null=True,default=0)
    revision = models.CharField(max_length=20, choices=REVISION_CHOICES, default='No Revision')
    reviewed_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = 'Laporan Penilaian'
        verbose_name_plural = 'Laporan Penilaian'
    def __str__(self):
        return f"{self.assesment.submission_apply.team.name} - Reviewed by : {self.assesment.reviewer.full_name}"

    def save(self, *args, **kwargs):
        self.calculate_final_score()
        if self.revision != 'No Revision':
            self.assesment.submission_apply.status = SubmissionsProposalApply.STATUS[3][0]
        else:
            self.assesment.submission_apply.status = SubmissionsProposalApply.STATUS[4][0]
        self.assesment.submission_apply.save()
        super(AssesmentReport, self).save(*args, **kwargs)

    def calculate_final_score(self):
        final_score = 0
        for stage_assessment in self.assesment.assessment_values_2.all():
            presentase_decimal = stage_assessment.key_assesment.presentase / 100
            final_score += stage_assessment.score * presentase_decimal
        self.final_score = final_score


@receiver(m2m_changed, sender=LecturerTeamSubmissionApply.submission_apply.through)
def update_assesments(sender, instance, action, **kwargs):
    if action == 'post_add':
        for submission in instance.submission_apply.all():
            assesment, created = AssesmentSubmissionsProposal.objects.get_or_create(submission_apply=submission, defaults={'reviewer': instance.lecturer})
            if not created:
                assesment.reviewer = instance.lecturer
                assesment.save()
                
    elif action == 'post_remove':
        for submission in instance.submission_apply.all():
            AssesmentSubmissionsProposal.objects.filter(submission_apply=submission, reviewer=instance.lecturer).delete()

@receiver(post_save, sender=AssesmentSubmissionsProposal)
def update_final_score(sender, instance, **kwargs):
    for report in instance.assesment_report.all():
        report.calculate_final_score()
        report.save()