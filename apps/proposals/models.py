import hashlib
from django.db import models
from django.db import models
from django.dispatch import receiver
from django.forms import ValidationError
from taggit.managers import TaggableManager
import os
from django.db.models.signals import m2m_changed, post_save, pre_save,post_delete

from utils.exceptions import failure_response_validation
from utils.handle_file_upload import UploadToPathAndRename

from decimal import Decimal


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
            self.slug = hashlib.sha256(self.title.encode('utf-8')).hexdigest()[:50]
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
    # lecturer = models.ForeignKey('account.Lecturer', related_name='submissions_proposals_apply', on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=200,unique=True)
    description = models.TextField(blank=True, null=True)
    tags = TaggableManager( related_name='submissions_proposals_apply')
    proposal = models.FileField(upload_to=UploadToPathAndRename(os.path.join('proposals', 'submission_proposal/apply')))
    slug = models.SlugField(unique=True, blank=True, null=True)
    def __str__(self):
        return f"{self.team.name} - {self.submission.title}"
    
    class Meta:
        verbose_name_plural = 'Proposal Mahasiswa'
        unique_together = ('team', 'submission',) 

    def save(self, *args, **kwargs):
        if not self.category:
            self.category = self.submission.program.scheme.first()

        if not self.slug:
            original_slug = hashlib.sha256(self.submission.title.encode('utf-8')).hexdigest()[:25]
            unique_slug = original_slug
            num = 1
            while SubmissionsProposalApply.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{original_slug}-{num}"
                num += 1
            self.slug = unique_slug

        if self.submission.title == 'REVISION':
            # If the application status is also "REVISION", bypass the period check
            if self.status == 'REVISION':
                super().save(*args, **kwargs)
                return

        # Existing logic to fetch the period of the current submission
        current_period = self.submission.program.period

        # Existing logic to check for existing applications by the same team for any submission within the same period
        existing_applications = SubmissionsProposalApply.objects.filter(
            team=self.team,
            submission__program__period=current_period
        ).exclude(id=self.id)  # Exclude the current instance to allow updates

        if existing_applications.exists():
            # If an existing application is found, raise a ValidationError
            raise ValidationError(f'The team {self.team.name} has already applied for a submission in the period {current_period}.')

        super().save(*args, **kwargs)



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
    submission_apply = models.ManyToManyField('proposals.SubmissionsProposalApply', related_name='lecturers')
    
    class Meta:
        verbose_name = 'Pembagian Team & Reviewer'

    def __init__(self, *args, **kwargs):
        super(LecturerTeamSubmissionApply, self).__init__(*args, **kwargs)
        # Store the original value of the lecturer field
        self.__original_lecturer = self.lecturer_id

    def clean(self):
        # Check if the instance is being added or the lecturer field has changed
        if self._state.adding or self.lecturer_id != self.__original_lecturer:
            if LecturerTeamSubmissionApply.objects.filter(lecturer=self.lecturer).exclude(pk=self.pk).exists():
                raise ValidationError({'lecturer': 'This lecturer is already associated with a team submission and cannot be added to another.'})
            
    def save(self, *args, **kwargs):
        self.full_clean()  
        super(LecturerTeamSubmissionApply, self).save(*args, **kwargs)
        self.submission_apply.set(self.submission_apply.all())

    def __str__(self):
        return f"Lecturer: {self.lecturer.full_name} - Submissions: {', '.join(str(sub) for sub in self.submission_apply.all())}"  

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
class AssesmentReview(models.Model):
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
        verbose_name = 'Review Penilaian'
        verbose_name_plural = 'Review Penilaian'
    def __str__(self):
        return f"{self.assesment.submission_apply.team.name} - Reviewed by : {self.assesment.reviewer.full_name}"

    def save(self, *args, **kwargs):
        self.calculate_final_score()
        if self.revision != 'No Revision':
            self.assesment.submission_apply.status = SubmissionsProposalApply.STATUS[3][0]
        else:
            self.assesment.submission_apply.status = SubmissionsProposalApply.STATUS[4][0]
        self.assesment.submission_apply.save()
        super(AssesmentReview, self).save(*args, **kwargs)



    def calculate_final_score(self):
        final_score = Decimal(0)  # Ensure final_score is a Decimal
        assessments = self.assesment.assessment_values_2.all()
        (f"Assessments: {assessments}")  # Debugging
        for stage_assessment in assessments:
            presentase_decimal = Decimal(stage_assessment.key_assesment.presentase) / 100
            final_score += Decimal(stage_assessment.score) * presentase_decimal
        self.final_score = final_score
        (f"Calculated Final Score: {final_score}")  # Debugging

class AssessmentReport(models.Model):
    assessment_submission_proposal = models.OneToOneField(AssesmentSubmissionsProposal, on_delete=models.CASCADE, related_name='assessment_report')
    stage_assessment_2 = models.ManyToManyField(StageAssesment2, related_name='assessment_report', blank=True)
    assessment_review = models.OneToOneField(AssesmentReview, on_delete=models.CASCADE, related_name='assessment_report', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Laporan Penilaian'
        verbose_name_plural = 'Laporan Penilaian'

    def __str__(self):
        return f"Report for {self.assessment_submission_proposal.submission_apply.team.name}"

    def calculate_stage_2_average_score(self):
        # Assuming there can be multiple StageAssessment2 records for a single proposal,
        # calculate the average score.
        stage_2_assessments = StageAssesment2.objects.filter(assesment=self.assessment_submission_proposal)
        if not stage_2_assessments:
            return 0
        total_score = sum(assessment.score for assessment in stage_2_assessments)
        return total_score / stage_2_assessments.count()
    def get_category(self):
        return self.assessment_submission_proposal.submission_apply.category




# @receiver(pre_save, sender=LecturerTeamSubmissionApply)
# def capture_old_values(sender, instance, **kwargs):
#     if instance.pk:
#         old_instance = sender.objects.get(pk=instance.pk)
#         instance._old_lecturer = old_instance.lecturer
#         instance._old_submission_apply = list(old_instance.submission_apply.all())

# @receiver(post_save, sender=LecturerTeamSubmissionApply)
# def update_assessments_on_change(sender, instance, created, **kwargs):
#     if created:
#         return  # Skip newly created instances

#     # Check if 'lecturer' has changed
#     if hasattr(instance, '_old_lecturer') and instance.lecturer != instance._old_lecturer:
#         # Update assessments with the new lecturer
#         AssesmentSubmissionsProposal.objects.filter(submission_apply__in=instance.submission_apply.all(), reviewer=instance._old_lecturer).update(reviewer=instance.lecturer)

#     # Check if 'submission_apply' has changed
#     if hasattr(instance, '_old_submission_apply'):
#         new_submissions = set(instance.submission_apply.all())
#         old_submissions = set(instance._old_submission_apply)

#         # Find removed submissions
#         removed_submissions = old_submissions - new_submissions
#         if removed_submissions:
#             AssesmentSubmissionsProposal.objects.filter(submission_apply__in=removed_submissions, reviewer=instance.lecturer).delete()

#         # Find added submissions
#         added_submissions = new_submissions - old_submissions
#         for submission in added_submissions:
#             AssesmentSubmissionsProposal.objects.get_or_create(submission_apply=submission, defaults={'reviewer': instance.lecturer})

# @receiver(m2m_changed, sender=LecturerTeamSubmissionApply.submission_apply.through)
# def update_assessments(sender, instance, action, reverse, pk_set, **kwargs):
#     if action == "post_add":
#         # Handle the case where submission applies are added to the lecturer team submission
#         for submission_apply_id in pk_set:
#             AssesmentSubmissionsProposal.objects.get_or_create(
#                 submission_apply_id=submission_apply_id,
#                 reviewer=instance.lecturer
#             )
#     elif action == "post_remove":
#         # Handle the case where submission applies are removed from the lecturer team submission
#         if reverse:
#             for submission_apply_id in pk_set:
#                 AssesmentSubmissionsProposal.objects.filter(
#                     submission_apply_id=submission_apply_id,
#                     reviewer=instance.lecturer
#                 ).delete()
#     elif action == "post_clear":
#         # Handle the case where all submission applies are removed from the lecturer team submission
#         if reverse:
#             AssesmentSubmissionsProposal.objects.filter(
#                 reviewer=instance.lecturer
#             ).delete()



@receiver(post_save, sender=AssesmentSubmissionsProposal)
def update_final_score(sender, instance, **kwargs):
    for report in instance.assesment_report.all():
        report.calculate_final_score()
        report.save()