from celery import shared_task
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.notification.models import Notification
from apps.pkm.models import PKMIdeaContribute, PKMIdeaContributeApplyTeam, PKMProgram
from apps.proposals.models import SubmissionsProposalApply
from utils.send_notification import BaseNotification

from datetime import timedelta
from django.utils import timezone


# signal pkm idea contribution : STUDENT,GUEST
@receiver(post_save, sender=PKMIdeaContribute)
def pkm_idea_contribute_notification(sender, instance, created, **kwargs):
    
    status_messages = {
        PKMIdeaContribute.STATUS_CHOICES[0][0]: f"PKM Idea Contribute {instance.title} has been submitted",
        PKMIdeaContribute.STATUS_CHOICES[1][0]: f"PKM Idea Contribute {instance.title} has been published",
        PKMIdeaContribute.STATUS_CHOICES[3][0]: f"PKM Idea Contribute {instance.title} has been rejected",
    }

    user = instance.user
    message = status_messages[instance.status]

    # BaseNotification(user, message).send_notification()
    Notification.objects.create(user=user, message=message)
@shared_task
def pkm_activity_schedule_notification():
    from apps.pkm.models import PKMActivitySchedule
    from datetime import timedelta, timezone

    # Send notifications 7 days (1 week) and 0 days (today) before the event
    for days in [0, 7]:
        upcoming_schedules = PKMActivitySchedule.objects.filter(
            start_date__gte=timezone.now() + timedelta(days=days),
            start_date__lt=timezone.now() + timedelta(days=days+1),
        )
        for schedule in upcoming_schedules:
            if days == 0:
                message = f"Activity Schedule {schedule.title} is starting today!"
            else:
                message = f"Activity Schedule {schedule.title} is starting in {days} days!"
            program = schedule.program

            # BaseNotification(program, message).send_notification()
            Notification.objects.create(user=program.user, message=message)

# signal pkm is ending : STUDENT
@shared_task
def pkm_ending_notification():
    from apps.pkm.models import PKMProgram
    from datetime import timedelta, timezone

    # Send notifications 7 days (1 week) and 0 days (today) before the event
    for days in [0, 7]:
        ending_programs = PKMProgram.objects.filter(
            end_date__gte=timezone.now() + timedelta(days=days),
            end_date__lt=timezone.now() + timedelta(days=days+1),
        )
        for program in ending_programs:
            if days == 0:
                message = f"{program.name} is ending today!"
            else:
                message = f"{program.name} is ending in {days} days!"

            # BaseNotification(program, message).send_notification()
            Notification.objects.create(user=program.user, message=message)

@shared_task
def delete_notifications_after_program_end():
  
    # Get programs that ended the day before yesterday
    ended_programs = PKMProgram.objects.filter(
        end_date__lt=timezone.now() - timedelta(days=1),
        end_date__gte=timezone.now() - timedelta(days=2),
    )

    for program in ended_programs:
        # Get the SubmissionProposalApply instances related to the program
        submission_proposals = SubmissionsProposalApply.objects.filter(submission_proposal=program.submission_proposal)

        for submission_proposal in submission_proposals:
            # Delete all notifications for the leader of the team associated with the SubmissionProposalApply
            Notification.objects.filter(user=submission_proposal.team.leader.user).delete()

            # Delete all notifications for the members of the team associated with the SubmissionProposalApply
            for member in submission_proposal.team.members.all():
                Notification.objects.filter(user=member.user).delete()


# signal pkm idea contribution team status : STUDENT

@receiver(post_save, sender=PKMIdeaContributeApplyTeam)
def pkm_idea_contribute_team_notification(sender, instance, created, **kwargs):
    status_messages = {
        PKMIdeaContributeApplyTeam.STATUS_CHOICES[0][0]: f"Your team application for Idea Contribute {instance.idea_contribute.title} has been submitted",
        PKMIdeaContributeApplyTeam.STATUS_CHOICES[1][0]: f"Your team application for Idea Contribute {instance.idea_contribute.title} has been accepted",
        PKMIdeaContributeApplyTeam.STATUS_CHOICES[2][0]: f"Your team application for Idea Contribute {instance.idea_contribute.title} has been rejected",
    }

    # Get the current time
    now = timezone.now()

    # If this is the first application for this idea contribute and it's been more than 3 days since it was created
    if instance.created < now - timezone.timedelta(days=3):
        first_application = PKMIdeaContributeApplyTeam.objects.filter(idea_contribute=instance.idea_contribute).order_by('created').first()

        # If this is the first application and its status is still 'Pending', accept it
        if instance == first_application and instance.status == 'P':
            instance.status = 'A'
            instance.save()

            # Reject all other applications for this idea contribute
            other_applications = PKMIdeaContributeApplyTeam.objects.filter(idea_contribute=instance.idea_contribute).exclude(pk=instance.pk)
            other_applications.update(status='R')

    user = instance.team.leader.user
    message = status_messages[instance.status]

    # BaseNotification(user, message).send_notification()
    Notification.objects.filter(user=user).update(message=message)

# signal pkm idea contribution team to owner : OWNER
@receiver(post_save, sender=PKMIdeaContributeApplyTeam)
def pkm_idea_contribute_team_owner_notification(sender, instance, created, **kwargs):
    if created:  # only for newly created instances
        Notification.objects.create(
            user=instance.idea_contribute.user,
            message=f"Team {instance.team.name} has applied to your idea {instance.idea_contribute.title}."
        )