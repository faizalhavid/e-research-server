from django import forms
from django.contrib import admin
from django.forms import BaseInlineFormSet, ModelForm, model_to_dict
from apps.account.models import Lecturer
from django.utils.html import format_html
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

class SubmissionProposalApplyForm(ModelForm):
    class Meta:
        model= SubmissionsProposalApply
        exclude = ('slug',)

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
    list_display = ('id', 'title', 'status', 'get_program_period')
    search_fields = ('title', 'status', 'program__period')  
    list_filter = ('status', 'program__period') 

    fieldsets = [
        ('Submissions Information', {
            'fields': ('title', 'description', 'status', 'program', 'due_time'),
        }),
        ('Advanced Informations', {
            'classes': ('collapse',),
            'fields': ('additional_file',), 
        }),
    ]
    

    def get_program_period(self, obj):
        return obj.program.period
    get_program_period.short_description = 'Program Period'  # Optional: Sets column header

    def program_name(self, obj):
        return obj.program.title
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




    class Meta:
        model = StageAssesment1
        fields = '__all__'



class StageAssesment1Inline(admin.TabularInline):
    model = StageAssesment1
    extra = 1

    

class StageAssesment2Inline(admin.TabularInline):
    model = StageAssesment2
    extra = 1
    

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
        print(obj)
        print(obj.submission_apply.proposal)  # This will print the proposal to the console
        proposal = obj.submission_apply.proposal if obj else None
        
        context.update({
            'request': request,
            'first_proposal': proposal,
        })
        return super().render_change_form(request, context, *args, **kwargs)
    
    def proposal_file_url(self, obj):
        proposal = obj.submission_apply.proposal
        if proposal and proposal.url:
            return format_html('<a href="{}" target="_blank" style="display: inline-block; padding: 6px 12px; background-color: #007bff; color: white; text-align: center; text-decoration: none; border-radius: 4px;">Download</a>', proposal.url)
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
        print(submission)
        team = submission.team
        proposal = submission.title
        if proposal is None:  # Check if proposal is not None
            return f"No proposal - {team}"
        return f"{proposal} - {team.leader.full_name}  ({team.name})"
    submission_information.short_description = 'Judul Proposal - Ketua Team'
    
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

