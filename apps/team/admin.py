from django.contrib import admin


from apps.account.models import Student
from apps.proposals.models import Proposal
from apps.team.models import Team, TeamApply, TeamVacanicies

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    model = Team
    list_display = ('name', 'description', 'leader', 'lecturer', 'status', 'created_at', 'updated_at', 'submission_information')
    search_fields = ('name', 'description', 'leader__user__username', 'lecturer__user__username', 'status')
    list_filter = ('status', 'created_at', 'updated_at')
    raw_id_fields = ('leader', 'lecturer')
    filter_horizontal = ('members',)

    def submission_information(self, obj):
        if Proposal.objects.filter(team=obj).exists():
            return Proposal.objects.get(team=obj).title
        else:
            return 'No Submission Proposal'
    submission_information.short_description = 'Submission'



@admin.register(TeamVacanicies)
class TeamVacaniciesAdmin(admin.ModelAdmin):
    model = TeamVacanicies
    list_display = ('id',  'description', 'role', 'team')
    search_fields = ( 'description', 'role', 'team__name')

@admin.register(TeamApply)
class TeamApplyAdmin(admin.ModelAdmin):
    model = TeamApply
    list_display = ('id', 'get_vacancies_role' , 'user', 'status')
    search_fields = ('team__name', 'user__email', 'status')
    
    def get_vacancies_role(self, obj):
        return obj.vacanicies.role
    get_vacancies_role.short_description = 'Vacancies Role'
