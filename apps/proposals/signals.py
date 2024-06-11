from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.notification.models import Notification
from apps.proposals.models import SubmissionsProposalApply
from apps.team.models import Team
from django.db import transaction

from django.contrib.contenttypes.models import ContentType
from utils.send_notification import BaseNotification



@receiver(post_save, sender=SubmissionsProposalApply)
def submission_proposal_apply_notification(sender, instance, created, **kwargs):
    status_messages = {
        SubmissionsProposalApply.STATUS[0][0]: ("Submission Proposal Apply {title} has been submitted", "info"),
        SubmissionsProposalApply.STATUS[1][0]: ("Submission Proposal Apply {title} has been accepted", "success"),
        SubmissionsProposalApply.STATUS[2][0]: ("Submission Proposal Apply {title} has been rejected", "error"),
        SubmissionsProposalApply.STATUS[3][0]: ("Submission Proposal Apply {title} has been revised, please check the revision !", "warning"),
        SubmissionsProposalApply.STATUS[4][0]: ("Submission Proposal Apply {title} has been approved", "success"),
        SubmissionsProposalApply.STATUS[5][0]: ("Congratulations, Submission Proposal Apply {title} has been passed funding !", "success"),
    }

    def create_notification(user, message, notif_type):
        return Notification(
            user=user,
            message=message.format(title=instance.title),
            type=notif_type,
            content_type=ContentType.objects.get_for_model(instance),
            object_id=instance.pk
        )

    # Gather users from team leader and members
    users = set(filter(None, [instance.team.leader.user] + [member.user for member in instance.team.members.all()]))

    # Create notifications for submission status
    message, notif_type = status_messages[instance.status]
    notifications = [create_notification(user, message, notif_type) for user in users]

    # Update team status and notify if applicable
    if instance.status in [SubmissionsProposalApply.STATUS[2][0], SubmissionsProposalApply.STATUS[4][0]]:
        instance.team.status = Team.STATUS_CHOICES[1][0]
        instance.team.save()
        new_message = f"Team {instance.team.name}'s status has been updated to {Team.STATUS_CHOICES[1][1]}"
        # Change content_type to Team for team status update notifications
        team_content_type = ContentType.objects.get_for_model(Team)
        team_notifications = [Notification(
            user=user,
            message=new_message,
            type="info",
            content_type=team_content_type,
            object_id=instance.team.pk
        ) for user in users]
        notifications += team_notifications
    
    # Bulk create notifications
    Notification.objects.bulk_create(notifications, ignore_conflicts=True)