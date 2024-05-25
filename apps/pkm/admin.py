from django.contrib import admin

from apps.pkm.models import PKMActivitySchedule, PKMIdeaContribute, PKMProgram, PKMScheme
from apps.proposals.models import SubmissionProposal

# Register your models here.


class SubmissionProposalInline(admin.TabularInline):
    model = SubmissionProposal
    extra = 0


@admin.register(PKMProgram)
class PKMProgramAdmin(admin.ModelAdmin):
    model = PKMProgram
    list_display = ('id', 'name')
    search_fields = ('name',)
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