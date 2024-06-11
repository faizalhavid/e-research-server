from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils import timezone
from django.core.handlers.wsgi import WSGIRequest
from apps.content_hub.admin import ArticleAdmin, NoticeAdmin
from apps.content_hub.models import Article, Notice
from apps.notification.admin import NotificationAdmin
from apps.notification.models import Notification
from apps.pkm.form import PeriodForm
from admincharts.admin import AdminChartMixin

from apps.account.models import *
from apps.account.admin import *

from apps.proposals.models import *
from apps.proposals.admin import *

from apps.pkm.models import *
from apps.pkm.form import *
from apps.pkm.admin import *
from apps.team.models import *
from apps.team.admin import *







class EReasearchAdminSite(admin.AdminSite, AdminChartMixin):
    site_header = 'E-Research Administration'
    site_title = 'E-Research Admin'
    index_title = 'E-Research Admin'
    site_url = 'http://localhost:3000'
    
    
    def index(self, request: WSGIRequest, extra_context=None):
        color = [
            {
                'DTE': 'red',
                'DTIK': 'blue',
                'DTMK': 'green',
                'DTME': 'yellow',
                
            }
        ]
        extra_context = extra_context or {}
        form = PeriodForm(request.GET)
        majors = Major.objects.all()
        extra_context['form'] = form
        periode_now = form.cleaned_data.get('period') if form.is_valid() else timezone.now().year

        pkm_participants_by_departement = [SubmissionsProposalApply.objects.filter(
            Q(team__members__department=department) | Q(team__leader__department=department),
            submission__program__period = periode_now,
            ).count() for department in Departement.objects.all()
        ]

        extra_context['list_chart_type'] = "pie"
        extra_context['list_chart_data'] = {
            "periode": f"{periode_now}",
            "labels": list({department.abbreviation for department in Departement.objects.all()}),
            "ruler": "PKM Participants per Department",
            "datasets": [
                {
                    "label": "PKM Participants",
                    "data": pkm_participants_by_departement,
                    "backgroundColor": [color[0][department.abbreviation] for department in Departement.objects.all()],
                    "tooltip": "PKM Participants", 
                }
            ],
        }
        datasets = [
            {
                "label": major.name,
                "data": [SubmissionsProposalApply.objects.filter(Q(team__members__major=major) | Q(team__leader__major=major),submission__program__period = periode_now).count()],
                "borderWidth": 0,
            }
            for major in majors
        ]

        extra_context['second_chart_type'] = "bar"
        extra_context['second_chart_data'] = {
            "periode": f"{periode_now}",
            "labels": [major.name for major in majors],
            "datasets": datasets,
        }
        
        insentif_pkm = ["PKM-GF", "PKM-AI"]
        pkm_8_category = PKMScheme.objects.exclude(abbreviation__in=insentif_pkm).values_list('abbreviation', flat=True)
        insentif_pkm_category = PKMScheme.objects.filter(abbreviation__in=insentif_pkm).values_list('abbreviation', flat=True)
        
        datasets = [
            {
                "label": "PKM 8 Category",
                "data": [SubmissionsProposalApply.objects.filter(category__abbreviation__exact=category, submission__program__period = periode_now).count() for category in pkm_8_category],
                "borderWidth": 0,
            },
            {
                "label": "Insentif PKM Category",
                "data": [SubmissionsProposalApply.objects.filter(category__abbreviation__exact=category, submission__program__period = periode_now).count() for category in insentif_pkm],
                "borderWidth": 0,
            }
        ]

        extra_context['third_chart_type'] = "doughnut"
        extra_context['third_chart_data'] = {
            "periode": f"{periode_now}",
            "labels": list(pkm_8_category) + list(insentif_pkm_category),
            "datasets": datasets,
        }
        return super().index(request, extra_context)



# for debug
# @admin.register(ContentType)
# class ContentTypeAdmin(admin.ModelAdmin):
#     list_display = ['id', 'app_label', 'model']
#     search_fields = ['app_label', 'model']
#     list_filter = ['app_label', 'model']
#     list_per_page = 10
#     list_max_show_all = 100
#     list_select_related = True

admin_site = EReasearchAdminSite(name='myadmin')


# admin_site.register(ContentType, ContentTypeAdmin)
admin_site.register(Group)
admin_site.register(User, UserAdmin)
admin_site.register(Student, StudentAdmin)
admin_site.register(Guest, GuestAdmin)
admin_site.register(Lecturer, LecturerAdmin)
admin_site.register(Departement, DepartmentAdmin)
admin_site.register(Major, MajorAdmin)

admin_site.register(Team, TeamAdmin)
admin_site.register(TeamVacancies, TeamVacanciesAdmin)
admin_site.register(TeamApply, TeamApplyAdmin)
admin_site.register(TeamTask, TeamTaskAdmin)

admin_site.register(PKMProgram, PKMProgramAdmin)
admin_site.register(PKMScheme, PKMSchemeAdmin)
admin_site.register(SubmissionProposal, SubmissionsProposalAdmin)
admin_site.register(SubmissionsProposalApply, SubmissionsProposalApplyAdmin)
# admin_site.register(Proposal, ProposalsAdmin)
admin_site.register(AssesmentSubmissionsProposal, AssesmentSubmissionsProposalAdmin)
admin_site.register(LecturerTeamSubmissionApply, LecturerTeamSubmissionApplyAdmin)
admin_site.register(StageAssesment1, StageAssesmenet1Admim)
admin_site.register(KeyStageAssesment1, KeyStageAssesment2Admin)
admin_site.register(StageAssesment2, StageAssesment2Admin)
admin_site.register(KeyStageAssesment2, KeyStageAssesment2Admin)
admin_site.register(PKMIdeaContribute, PKMIdeaContributeAdmin)
admin_site.register(PKMIdeaContributeApplyTeam, PKMIdeaContributeApplyTeamAdmin)
admin_site.register(PKMActivitySchedule, PKMActivity)

admin_site.register(Notice, NoticeAdmin)
admin_site.register(Article, ArticleAdmin)

admin_site.register(Notification, NotificationAdmin)



