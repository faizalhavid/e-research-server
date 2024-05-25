# signal team apply : STUDENT
from datetime import timedelta, timezone
from celery import shared_task
from apps.notification.models import Notification
from apps.team.models import TeamApply, TeamTask
from utils.send_notification import BaseNotification


def team_apply_notification(sender, instance, created, **kwargs):
    status_messages = {
        TeamApply.STATUS[0][0]: f"Team Apply {instance.vacancies.team.name} has been submitted",
        TeamApply.STATUS[1][0]: f"Team Apply {instance.vacancies.team.name} has been accepted",
        TeamApply.STATUS[2][0]: f"Team Apply {instance.vacancies.team.name} has been rejected",
    }
    user = instance.user
    message = status_messages[instance.status]
    
    BaseNotification(user, message).send_notification()
    Notification.objects.create(user=user, message=message)


# signal team task : STUDENT
@shared_task
def send_upcoming_deadline_notifications():
    for days in range(3):
        upcoming_tasks = TeamTask.objects.filter(
            due_time__gte=timezone.now() + timedelta(days=days),
            due_time__lt=timezone.now() + timedelta(days=days+1),
            completed=False
        )
        for task in upcoming_tasks:
            if days == 0:
                message = f"Task {task.title} is due today!"
            else:
                message = f"Task {task.title} is due in {days} days!"
            leader = task.team.leader
            members = task.team.members.all()

            BaseNotification(leader, message).send_notification()
            Notification.objects.create(user=leader.user, message=message)
            if members:
                for member in members:
                    BaseNotification(member, message).send_notification()
                    Notification.objects.create(user=member.user, message=message)


