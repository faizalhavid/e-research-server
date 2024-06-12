from django.contrib import admin

from apps.pkm.models import PKMActivitySchedule, PKMIdeaContribute, PKMIdeaContributeApplyTeam, PKMProgram, PKMScheme
from apps.proposals.models import SubmissionProposal
from django import forms

# Register your models here.


class SubmissionProposalInline(admin.TabularInline):
    model = SubmissionProposal
    extra = 0


@admin.register(PKMProgram)
class PKMProgramAdmin(admin.ModelAdmin):
    model = PKMProgram
    list_display = ('id', 'period')
    search_fields = ('period',)
    inlines = [SubmissionProposalInline]

@admin.register(PKMActivitySchedule)
class PKMActivity(admin.ModelAdmin):
    model = PKMActivitySchedule
    list_display = ('id', 'title')
    search_fields = ('title',)

@admin.register(PKMScheme)
class PKMSchemeAdmin(admin.ModelAdmin):
    model = PKMScheme
    list_display = ('id', 'name', 'description')
    search_fields = ('name', 'description', )


@admin.register(PKMIdeaContribute)
class PKMIdeaContributeAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'created']
    search_fields = ['title', 'description']

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['problem'].help_text = 'Enter problems as a comma-separated list, example: Problem 1, Problem 2'
        form.base_fields['solution'].help_text = 'Enter solutions as a comma-separated list, example: Solution 1, Solution 2'
        return form
    
@admin.register(PKMIdeaContributeApplyTeam)
class PKMIdeaContributeApplyTeamAdmin(admin.ModelAdmin):
    list_display = ['team', 'idea_contribute', 'status']
    search_fields = ['team__name', 'idea_contribute__title', 'status']