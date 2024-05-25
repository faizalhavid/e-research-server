from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.notification.models import Notification
from apps.proposals.models import SubmissionsProposalApply
from utils.send_notification import BaseNotification


# signal submission proposal apply : STUDENT
@receiver(post_save, sender=SubmissionsProposalApply)
def submission_proposal_apply_notification(sender, instance, created, **kwargs):
    
    status_messages = {
        SubmissionsProposalApply.STATUS[0][0]: f"Submission Proposal Apply {', '.join(proposal.title for proposal in instance.team.proposals.all())} has been submitted",
        SubmissionsProposalApply.STATUS[1][0]: f"Submission Proposal Apply {', '.join(proposal.title for proposal in instance.team.proposals.all())} has been rejected",
        SubmissionsProposalApply.STATUS[2][0]: f"Submission Proposal Apply {', '.join(proposal.title for proposal in instance.team.proposals.all())} has been accepted",
        SubmissionsProposalApply.STATUS[3][0]: f"Submission Proposal Apply {', '.join(proposal.title for proposal in instance.team.proposals.all())} has been revised, please check the revision !",
        SubmissionsProposalApply.STATUS[4][0]: f"Submission Proposal Apply {', '.join(proposal.title for proposal in instance.team.proposals.all())} has been approved",
        SubmissionsProposalApply.STATUS[5][0]: f"Congratulations, Submission Proposal Apply {', '.join(proposal.title for proposal in instance.team.proposals.all())} has been passed funding !",
    }

    leader = instance.team.leader
    members = instance.team.members.all()
    message = status_messages[instance.status]

    BaseNotification(leader, message).send_notification()
    Notification.objects.create(user=leader.user, message=message)
    if members:
        for member in members:
            BaseNotification(member, message).send_notification()
            Notification.objects.create(user=member.user, message=message)
