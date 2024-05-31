from django.contrib import admin
from django.forms import BaseInlineFormSet, model_to_dict
from apps.account.models import Lecturer
from django.utils.html import format_html

from apps.proposals.form import StageAssesment1Form, StageAssesment1InlineFormSet, StageAssesment2Form
from apps.proposals.models import *




@admin.register(LecturerTeamSubmissionApply)
class LecturerTeamSubmissionApplyAdmin(admin.ModelAdmin):
    model = LecturerTeamSubmissionApply
    list_display = ('lecturer','submission_information', )

    def submission_information(self, obj):
        submission_info = []
        for submission in obj.submission_apply.all():
            team = submission.team
            submission_info.append(f"{team.name}")
        return ", ".join(submission_info)
    submission_information.short_description = 'Teams for reviewer'

@admin.register(SubmissionsProposalApply)
class SubmissionsProposalApplyAdmin(admin.ModelAdmin):
    model = SubmissionsProposalApply
    list_display = ('id', 'submission_information', 'lecturer', 'status')
    search_fields = ('submission__title', 'title', 'status')
    list_display_links = ('id', 'submission_information')
    list_editable = ['status']

    def submission_information(self, obj):
        return f"{obj.team.name} - {obj.title}"

@admin.register(SubmissionProposal)
class SubmissionsProposalAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'status', 'program_name')
    search_fields = ('title', 'status', 'program__name')  
    list_filter = ('status', 'program__name') 

    def program_name(self, obj):
        return obj.program.name
    program_name.short_description = 'Program'



# @admin.register(Proposal)
# class ProposalsAdmin(admin.ModelAdmin):
#     model = Proposal
#     list_display = ('id', 'title')
#     search_fields = ['title']

#     def tag_list(self, obj):
#         return u", ".join(o.name for o in obj.tags.all())


       
@admin.register(KeyStageAssesment1)
class KeyStageAssesment1Admin(admin.ModelAdmin):
    model = KeyStageAssesment1
    list_display = ('id', 'title')
      
@admin.register(KeyStageAssesment2)
class KeyStageAssesment2Admin(admin.ModelAdmin):
    model = KeyStageAssesment2
    list_display = ('id', 'title')


class PrePopulatedFormSet(BaseInlineFormSet):
    def get_initial(self):
        initial = super().get_initial()
        if self.queryset.exists():
            initial.extend(model_to_dict(instance) for instance in self.queryset)
        return initial

    def get_queryset(self):
        if not hasattr(self, '_queryset'):
            criteria = {}  # Your criteria here
            qs = super().get_queryset().filter(**criteria)
            self._queryset = qs
        return self._queryset

class StageAssesment1Inline(admin.TabularInline):
    model = StageAssesment1
    formset = PrePopulatedFormSet
    

class StageAssesment2Inline(admin.TabularInline):
    model = StageAssesment2
    formset = PrePopulatedFormSet
    

@admin.register(AssesmentSubmissionsProposal)
class AssesmentSubmissionsProposalAdmin(admin.ModelAdmin):
    change_form_template = 'admin/assesmentProposal/assesmentForm.html'
    list_display = ('submission_information', 'status_colored', 'reviewer', 'reviewed_at')
    list_editable = ('reviewer',)
    list_filter = ('submission_apply__submission__title', 'reviewer')
    inlines = [StageAssesment1Inline, StageAssesment2Inline]
    model = AssesmentSubmissionsProposal
    search_fields = ('submission_apply__submission__title', 'reviewer__full_name', 'status')
    readonly_fields = ('reviewed_at', 'proposal_file_url')  # Add proposal_file_url here
    fieldsets = (
        ('Proposal Mahasiswa', {
            'fields': ('submission_apply', 'reviewer',  'reviewed_at', 'proposal_file_url'),
        }),
    )
    list_display_links = ['submission_information']  

    def render_change_form(self, request, context, *args, **kwargs):
        obj = kwargs.get('obj')
        proposal = obj.submission_apply.team.proposals.first() if obj else None
        
        context.update({
            'request': request,
            'first_proposal': proposal,
        })
        return super().render_change_form(request, context, *args, **kwargs)
    
    def proposal_file_url(self, obj):
        proposal = obj.submission_apply.team.proposals.first()
        print(f'Proposal: {proposal}')  # This will print the proposal to the console
        if proposal and proposal.file:
            print(f'File: {proposal.file}')  # This will print the file to the console
            return proposal.file
        else:
            return 'No file'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.groups.filter(name='LecturerReviewer').exists():
            lecturer = Lecturer.objects.get(user=request.user)
            return qs.filter(reviewer=lecturer)
        return qs

    def submission_information(self, obj):
        submission = obj.submission_apply
        team = submission.team
        proposal = team.proposals.first()
        if proposal is None:  # Check if proposal is not None
            return f"No proposal - {team}"
        return f"{proposal.title} - {team}"
    
    def status_colored(self, obj):
        color = 'red' if obj.submission_apply.status == 'Rejected' else 'green'
        return format_html('<span style="color: {};">{}</span>', color, obj.submission_apply.status)
    status_colored.short_description = 'Status'

@admin.register(StageAssesment1)
class StageAssesmenet1Admim(admin.ModelAdmin):
    model = StageAssesment1
    list_display = ('id','team_reviewed')
    
    def changelist_view(self, request, *args, **kwargs):
        self.request = request
        return super().changelist_view(request, *args, **kwargs)

    def team_reviewed(self, obj):
        assesments = AssesmentSubmissionsProposal.objects.filter(reviewer__user=self.request.user)
        submissions = [assesment.submission_apply for assesment in assesments]
        team = [submission.team for submission in submissions]
        return team
        
    team_reviewed.short_description = 'Team Reviewed'

@admin.register(StageAssesment2)
class StageAssesment2Admin(admin.ModelAdmin):
    model = StageAssesment2
    list_display = ('id','get_assesment_title', 'key_assesment',  'score')

    def get_assesment_title(self, obj):
        return f"{obj.assesment.submission_apply.proposal.title} - {obj.assesment.submission_apply.proposal.team}"
    get_assesment_title.short_description = 'Assesment Title' 
     # Sets column header in admin site


    

class LecturerSubmissionApplyListFilter(admin.SimpleListFilter):
    title = 'lecturer'
    parameter_name = 'lecturer'

    def lookups(self, request, model_admin):
        lecturers = Lecturer.objects.all()
        return [(lecturer.id, lecturer.name) for lecturer in lecturers]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(lecturer__id=self.value())
        else:
            return queryset

