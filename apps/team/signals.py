# signal team apply : STUDENT
from datetime import timedelta, timezone
from celery import shared_task
from apps.account.models import User
from apps.notification.models import Notification
from apps.team.models import TeamApply, TeamTask
from utils.send_notification import BaseNotification
from django.db.models import Prefetch


from django.contrib.contenttypes.models import ContentType

def team_apply_notification(sender, instance, created, **kwargs):
    status_messages = {
        TeamApply.STATUS[0][0]: ("Team Apply {team_name} has been submitted", 'info'),
        TeamApply.STATUS[1][0]: ("Team Apply {team_name} has been accepted", 'success'),
        TeamApply.STATUS[2][0]: ("Team Apply {team_name} has been rejected", 'error'),
    }
    user = instance.user
    team_name = instance.vacancies.team.name
    message, notif_type = status_messages[instance.status][0].format(team_name=team_name), status_messages[instance.status][1]
    
    # Fetch the ContentType for TeamApply
    content_type = ContentType.objects.get_for_model(TeamApply)
    
    # Create a Notification instance with content_type and object_id
    Notification.objects.create(
        user=user, 
        message=message, 
        type=notif_type,
        content_type=content_type, 
        object_id=instance.id
    )


@shared_task
def send_upcoming_deadline_notifications():
    for days in range(3):
        upcoming_tasks = TeamTask.objects.filter(
            due_time__gte=timezone.now() + timedelta(days=days),
            due_time__lt=timezone.now() + timedelta(days=days+1),
            completed=False
        ).select_related('team__leader').prefetch_related(
            Prefetch('team__members', queryset=User.objects.exclude(id=F('team__leader__id')))
        )

        notifications = []
        for task in upcoming_tasks:
            message = f"Task {task.title} is due today!" if days == 0 else f"Task {task.title} is due in {days} days!"
            notification_type = 'reminder'

            # Notify the team leader
            notifications.append(Notification(user=task.team.leader.user, message=message, type=notification_type))

            # Notify team members
            members = task.team.members.all()  # Assuming leader is already excluded in the prefetch_related
            for member in members:
                notifications.append(Notification(user=member.user, message=message, type=notification_type))

        # Bulk create notifications
        Notification.objects.bulk_create(notifications)