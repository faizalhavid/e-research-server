from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, Count
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

        pkm_participants_by_departement = []

        for department in Departement.objects.all():

            member_count = SubmissionsProposalApply.objects.filter(
                Q(team__members__department=department),
                submission__program__period=periode_now
            ).values('team__members').annotate(member_count=Count('team__members')).count()

            # Menghitung jumlah leader berdasarkan departemen
            leader_count = SubmissionsProposalApply.objects.filter(
                Q(team__leader__department=department),
                submission__program__period=periode_now
            ).values('team__leader').annotate(leader_count=Count('team__leader')).count()


            total_count = member_count + leader_count
            pkm_participants_by_departement.append(total_count)
        extra_context['list_chart_type'] = "pie"
        extra_context['list_chart_data'] = {
            "periode": f"{periode_now}",
            "labels": list({department.abbreviation for department in Departement.objects.all()}),
            "ruler": "PKM Participants per Department",
            "datasets": [
                {
                    "label": "PKM Participants",
                    "data": pkm_participants_by_departement,
                    "backgroundColor": [departement.color for departement in Departement.objects.all()],
                    "tooltip": "PKM Participants", 
                }
            ],
        }
        
        datasets = []

        for major in majors:
            member_count = SubmissionsProposalApply.objects.filter(
                Q(team__members__major=major),
                submission__program__period=periode_now
            ).values('team__members').annotate(member_count=Count('team__members')).count()

            leader_count = SubmissionsProposalApply.objects.filter(
                Q(team__leader__major=major),
                submission__program__period=periode_now
            ).values('team__leader').annotate(leader_count=Count('team__leader')).count()

            total_count = member_count + leader_count

            datasets.append({
                "label": major.abbreviation,
                "data": [total_count],
                "borderWidth": 0,
            })
                
        extra_context['second_chart_type'] = "bar"
        extra_context['second_chart_data'] = {
            "periode": f"{periode_now}",
            "labels": [major.abbreviation for major in majors],
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
                "backgroundColor": [
                    'rgb(255, 99, 132)',
                    'rgb(255, 159, 64)',
                    'rgb(255, 205, 86)',
                    'rgb(75, 192, 192)',
                    'rgb(54, 162, 235)',
                    'rgb(153, 102, 255)',
                    'rgb(201, 203, 207)',
                    'rgb(255, 99, 132)',
                    'rgb(255, 159, 64)',
                    'rgb(255, 205, 86)',

                ],
                "borderColor": [
                    'rgb(255, 99, 132)',
                    'rgb(255, 159, 64)',
                    'rgb(255, 205, 86)',
                    'rgb(75, 192, 192)',
                    'rgb(54, 162, 235)',
                    'rgb(153, 102, 255)',
                    'rgb(201, 203, 207)'
                ],
            },
            {
                "label": "Insentif PKM Category",
                "data": [SubmissionsProposalApply.objects.filter(category__abbreviation__exact=category, submission__program__period = periode_now).count() for category in insentif_pkm],
                "borderWidth": 0,
                "backgroundColor": [
                     'rgb(113, 88, 143)',  # Purple
                     'rgb(234, 76, 137)',
                ],
                "borderColor": [
                     'rgb(113, 88, 143)',  # Purple
                    'rgb(234, 76, 137)', 
                ],
            }
        ]

        extra_context['third_chart_type'] = "doughnut"
        extra_context['third_chart_data'] = {
            "periode": f"{periode_now}",
            "labels": list(pkm_8_category) + list(insentif_pkm_category),
            "datasets": datasets,
        }
        
        # Notice
        extra_context['notices'] = Notice.objects.all().order_by('-created')[:5]
        
        # PKM Schedule
        extra_context['pkm_schedule'] = PKMActivitySchedule.objects.all().order_by('-start_date')[:5]


        
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
admin_site.register(StageAssesment1, StageAssesment1Admin)
admin_site.register(KeyStageAssesment1, KeyStageAssesment1Admin)
admin_site.register(StageAssesment2, StageAssesment2Admin)
admin_site.register(AssessmentReport, AssessmentReportAdmin)
admin_site.register(KeyStageAssesment2, KeyStageAssesment2Admin)
admin_site.register(PKMIdeaContribute, PKMIdeaContributeAdmin)
admin_site.register(PKMIdeaContributeApplyTeam, PKMIdeaContributeApplyTeamAdmin)
admin_site.register(PKMActivitySchedule, PKMActivity)

admin_site.register(Notice, NoticeAdmin)
admin_site.register(Article, ArticleAdmin)

admin_site.register(Notification, NotificationAdmin)



