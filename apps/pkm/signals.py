import logging
from celery import shared_task
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.notification.models import Notification
from apps.pkm.models import PKMActivitySchedule, PKMIdeaContribute, PKMIdeaContributeApplyTeam, PKMProgram
from apps.proposals.models import SubmissionsProposalApply
from utils.send_notification import BaseNotification
from django.contrib.contenttypes.models import ContentType
from datetime import timedelta
from django.utils import timezone


# signal pkm idea contribution : STUDENT,GUEST
@receiver(post_save, sender=PKMIdeaContribute)
def pkm_idea_contribute_notification(sender, instance, created, **kwargs):
    
    status_messages_and_types = {
        PKMIdeaContribute.STATUS_CHOICES[0][0]: ("PKM Idea Contribute {title} has been submitted", 'info'),
        PKMIdeaContribute.STATUS_CHOICES[1][0]: ("PKM Idea Contribute {title} has been published", 'success'),
        PKMIdeaContribute.STATUS_CHOICES[3][0]: ("PKM Idea Contribute {title} has been rejected", 'error'),
    }

    user = instance.user
    message, notif_type = status_messages_and_types[instance.status]
    message = message.format(title=instance.title)

    # Get ContentType for PKMIdeaContribute
    content_type = ContentType.objects.get_for_model(instance)

    Notification.objects.create(
        user=user, 
        message=message, 
        type=notif_type,
        content_type=content_type,
        object_id=instance.id
    )


@shared_task
def pkm_activity_schedule_notification():
    # Send notifications 7 days (1 week) and 0 days (today) before the event
    for days in [0, 7]:
        upcoming_schedules = PKMActivitySchedule.objects.filter(
            start_date__gte=timezone.now() + timedelta(days=days),
            start_date__lt=timezone.now() + timedelta(days=days+1),
        )
        for schedule in upcoming_schedules:
            if days == 0:
                message = f"Activity Schedule {schedule.title} is starting today!"
                notif_type = 'info'  # Example type for same-day notification
            else:
                message = f"Activity Schedule {schedule.title} is starting in {days} days!"
                notif_type = 'warning'  # Example type for upcoming notification
            program = schedule.program

            # Get ContentType for PKMActivitySchedule
            content_type = ContentType.objects.get_for_model(schedule)

            Notification.objects.create(
                user=program.user, 
                message=message, 
                type=notif_type,
                content_type=content_type,
                object_id=schedule.id
            )

def pkm_ending_notification():
    # Send notifications 7 days (1 week) and 0 days (today) before the event
    for days in [0, 7]:
        ending_programs = PKMProgram.objects.filter(
            end_date__gte=timezone.now() + timedelta(days=days),
            end_date__lt=timezone.now() + timedelta(days=days+1),
        )
        for program in ending_programs:
            if days == 0:
                message = f"PKM{program.period} is ending today!"
                notif_type = 'info'  # Example type for same-day notification
            else:
                message = f"PKM{program.period} is ending in {days} days!"
                notif_type = 'warning'  # Example type for upcoming notification

            # Get ContentType for PKMProgram
            content_type = ContentType.objects.get_for_model(program)

            Notification.objects.create(
                user=program.user, 
                message=message, 
                type=notif_type,
                content_type=content_type,
                object_id=program.id
            )


@shared_task
def delete_notifications_after_program_end():
    from django.db.models import Q

    # Get programs that ended the day before yesterday
    ended_programs = PKMProgram.objects.filter(
        end_date__lt=timezone.now() - timedelta(days=1),
        end_date__gte=timezone.now() - timedelta(days=2),
    )

    user_ids = set()

    # Collect user IDs from leaders and members
    for program in ended_programs:
        submission_proposals = SubmissionsProposalApply.objects.filter(
            submission_proposal=program.submission_proposal
        ).select_related('team__leader').prefetch_related('team__members')

        for submission_proposal in submission_proposals:
            user_ids.add(submission_proposal.team.leader.user_id)
            user_ids.update(submission_proposal.team.members.values_list('user_id', flat=True))

    # Bulk delete notifications for all collected user IDs
    if user_ids:
        Notification.objects.filter(user_id__in=user_ids).delete()



# signal pkm idea contribution team status : STUDENT


@receiver(post_save, sender=PKMIdeaContributeApplyTeam)
def pkm_idea_contribute_team_notification(sender, instance, created, **kwargs):
    status_messages = {
        PKMIdeaContributeApplyTeam.STATUS_CHOICES[0][0]: ("Your team application for Idea Contribute {title} has been submitted", 'info'),
        PKMIdeaContributeApplyTeam.STATUS_CHOICES[1][0]: ("Your team application for Idea Contribute {title} has been accepted", 'success'),
        PKMIdeaContributeApplyTeam.STATUS_CHOICES[2][0]: ("Your team application for Idea Contribute {title} has been rejected", 'error'),
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
    message, notif_type = status_messages[instance.status][0].format(title=instance.idea_contribute.title), status_messages[instance.status][1]

    # Get ContentType for PKMIdeaContributeApplyTeam
    content_type = ContentType.objects.get_for_model(instance)

    # Create a new notification with the type field, content_type, and object_id
    Notification.objects.create(
        user=user, 
        message=message, 
        type=notif_type,
        content_type=content_type,
        object_id=instance.id
    )


@receiver(post_save, sender=PKMIdeaContributeApplyTeam)
def pkm_idea_contribute_team_owner_notification(sender, instance, created, **kwargs):
    if created:
        try:
            # Fetch the ContentType for PKMIdeaContributeApplyTeam
            content_type = ContentType.objects.get_for_model(PKMIdeaContributeApplyTeam)
            if content_type:
                # Create a Notification instance for the team leader
                Notification.objects.create(
                    user=instance.team.leader.user,
                    message=f"Your PKM Idea Contribute Apply Team '{instance.idea_contribute.title}' has been created.",
                    content_type=content_type,
                    object_id=instance.id
                )
                # Create a Notification instance for the idea contributor
                Notification.objects.create(
                    user=instance.idea_contribute.user,
                    message=f"Team {instance.team.name} has applied to your idea {instance.idea_contribute.title}.",
                    type='info'  # Assuming 'info' is a valid type in your Notification model
                )
            else:
                logging.error("ContentType for PKMIdeaContributeApplyTeam is null.")
        except ContentType.DoesNotExist:
            logging.error("ContentType for PKMIdeaContributeApplyTeam does not exist.")