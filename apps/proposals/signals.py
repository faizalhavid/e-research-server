from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.notification.models import Notification
from apps.proposals.models import SubmissionsProposalApply
from apps.team.models import Team
from utils.send_notification import BaseNotification


@receiver(post_save, sender=SubmissionsProposalApply)
def submission_proposal_apply_notification(sender, instance, created, **kwargs):
    
    status_messages = {
        SubmissionsProposalApply.STATUS[0][0]: f"Submission Proposal Apply {instance.title} has been submitted",
        SubmissionsProposalApply.STATUS[1][0]: f"Submission Proposal Apply {instance.title} has been rejected",
        SubmissionsProposalApply.STATUS[2][0]: f"Submission Proposal Apply {instance.title} has been accepted",
        SubmissionsProposalApply.STATUS[3][0]: f"Submission Proposal Apply {instance.title} has been revised, please check the revision !",
        SubmissionsProposalApply.STATUS[4][0]: f"Submission Proposal Apply {instance.title} has been approved",
        SubmissionsProposalApply.STATUS[5][0]: f"Congratulations, Submission Proposal Apply {instance.title} has been passed funding !",
    }

    leader = instance.team.leader
    members = instance.team.members.all()
    message = status_messages[instance.status]

    #BaseNotification(leader, message).send_notification()
    Notification.objects.create(user=leader.user, message=message)
    if members:
        for member in members:
            # BaseNotification(member, message).send_notification()
            Notification.objects.create(user=member.user, message=message)

    # Update team status and create new notification if instance status is 2 or 4
    if instance.status in [SubmissionsProposalApply.STATUS[2][0], SubmissionsProposalApply.STATUS[4][0]]:
        instance.team.status = Team.STATUS_CHOICES[1][0]
        instance.team.save()
        new_message = f"Team {instance.team.name}'s status has been updated to {Team.STATUS_CHOICES[1][1]}"
        # BaseNotification(leader, new_messsage).send_notification()
        Notification.objects.create(user=leader.user, message=new_message)
        if members:
            for member in members:
                # BaseNotification(member, new_message).send_notification()
                Notification.objects.create(user=member.user, message=new_message)