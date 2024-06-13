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
    list_display = ('id', 'title', 'category_display', 'presentase')


    def category_display(self, obj):
        return ", ".join([category.name for category in obj.category.all()])
    category_display.short_description = 'Categories'  # Optional: Sets the column header


class StageAssesment1Form(forms.ModelForm):

    key_assesment = forms.ModelChoiceField(queryset=KeyStageAssesment1.objects.all(), widget=forms.Select(attrs={'class': 'custom-select'}))
    class Meta:
        model = StageAssesment1
        fields = ['key_assesment', 'status']
        

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['key_assesment'].widget.attrs['class'] = 'custom-select'
        self.fields['key_assesment'].widget.attrs.update({
            'class': 'custom-select',
            'style': 'width:800px;word-wrap: break-word;height:900px!important;padding: 10px 10px!important;'
        })
        if self.instance and self.instance.pk:
            self.fields['key_assesment'].disabled = True
        if 'initial' in kwargs and 'key_assesment' in kwargs['initial']:
            self.fields['key_assesment'].disabled = True

class StageAssesment1Inline(admin.TabularInline):
    model = StageAssesment1
    form = StageAssesment1Form
    can_delete = False


    def get_formset(self, request, obj=None, **kwargs):
        key_assesments = KeyStageAssesment1.objects.all()
        key_assesment_count = key_assesments.count()
        self.extra = key_assesment_count if key_assesment_count > 0 else 1
        self.max_num = key_assesment_count

        initial = [{'key_assesment': key_assesment.id} for key_assesment in key_assesments]
        formset_class = super().get_formset(request, obj, **kwargs)

        class CustomFormSet(formset_class):
            def __init__(self, *args, **kwargs):
                kwargs['initial'] = initial
                super().__init__(*args, **kwargs)
                for form, initial_data in zip(self.forms, initial):
                    if not form.is_bound and not hasattr(form, 'instance') or not form.instance.pk:
                        form.initial = initial_data

        return CustomFormSet 


class StageAssesment2Form(forms.ModelForm):
    key_assesment = forms.ModelChoiceField(queryset=KeyStageAssesment2.objects.all(), widget=forms.Select(attrs={'class': 'custom-select'}))
    class Meta:
        model = StageAssesment2
        fields = ['key_assesment', 'score']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['key_assesment'].widget.attrs['class'] = 'custom-select'
        self.fields['key_assesment'].widget.attrs.update({
            'class': 'custom-select',
            'style': 'width: 800px;' 
        })
        initial = kwargs.get('initial')
  
        if self.instance and self.instance.pk:
            self.fields['key_assesment'].disabled = True
        if 'initial' in kwargs and 'key_assesment' in kwargs['initial']:
            self.fields['key_assesment'].disabled = True


class StageAssesment2Inline(admin.TabularInline):
    model = StageAssesment2
    form = StageAssesment2Form
    can_delete = False

    def get_formset(self, request, obj=None, **kwargs):
        key_assesments = KeyStageAssesment2.objects.filter(category=obj.submission_apply.category)
        key_assesment_count = key_assesments.count()
        self.extra = key_assesment_count if key_assesment_count > 0 else 1
        self.max_num = key_assesment_count
        print(key_assesment_count, self.extra, self.max_num)
    
        initial = [{'key_assesment': key_assesment.id} for key_assesment in key_assesments]
        formset_class = super().get_formset(request, obj, **kwargs)
        form = formset_class.form
        widget = form.base_fields['key_assesment'].widget
        widget.can_add_related = False
        widget.can_change_related = False
        widget.can_delete_related = False
        class CustomFormSet(formset_class):
            def __init__(self, *args, **kwargs):
                kwargs['initial'] = initial
                super().__init__(*args, **kwargs)
                for form, initial_data in zip(self.forms, initial):
                    if not form.is_bound and not hasattr(form, 'instance') or not form.instance.pk:
                        form.initial = initial_data 
    
        return CustomFormSet  
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "key_assesment":
            if request._obj_ is not None:

                submisson_apply = request._obj_.submission_apply
                kwargs["queryset"] = KeyStageAssesment2.objects.filter(category=submisson_apply.category)
            else:
                kwargs["queryset"] = KeyStageAssesment2.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class AssesmentReportInline(admin.TabularInline):
    model = AssesmentReport
    extra = 1
    max_num = 1

@admin.register(AssesmentSubmissionsProposal)
class AssesmentSubmissionsProposalAdmin(admin.ModelAdmin):

    def get_form(self, request, obj=None, **kwargs):
        request._obj_ = obj
        return super(AssesmentSubmissionsProposalAdmin, self).get_form(request, obj, **kwargs)
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        # Ensure the formset is valid
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                # Ensure all required fields are set or have defaults
                instance.assesment = form.instance
                # Debugging: Print or log instance to ensure it's correct
                print("Saving instance:", instance)
                instance.save()
            # Save many-to-many fields
            formset.save_m2m()
            super().save_formset(request, form, formset, change)
        else:
            # Debugging: Print or log formset errors
            print("Formset is not valid:", formset.errors)

    
    inlines = [StageAssesment1Inline, StageAssesment2Inline, AssesmentReportInline]
    change_form_template = 'admin/assesmentProposal/assesmentForm.html'
    list_display = ('submission_information', 'status_colored', 'reviewer', 'reviewed_at')
    list_editable = ('reviewer',)
    list_filter = ('submission_apply__submission__title', 'reviewer')
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
        rendered_form = super().render_change_form(request, context, *args, **kwargs)
        
        obj = kwargs.get('obj')
        proposal = obj.submission_apply.proposal if obj else None
        
        context.update({
            'request': request,
            'first_proposal': proposal,
        })
        
        return rendered_form

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
class StageAssesment1Admin(admin.ModelAdmin):
    model = StageAssesment1
    list_display = ('id', 'team_reviewed')

    def changelist_view(self, request, *args, **kwargs):
        self.request = request
        return super().changelist_view(request, *args, **kwargs)

    def team_reviewed(self, obj):
        assesments = AssesmentSubmissionsProposal.objects.filter(reviewer__user=self.request.user)
        submissions = [assesment.submission_apply for assesment in assesments]
        team = [submission.team for submission in submissions]
        return team

    team_reviewed.short_description = 'Team Reviewed'

    def get_model_perms(self, request):
        """
        Return empty perms dict if user is not superuser, thus hiding the model from admin index.
        """
        if request.user.is_superuser:
            return super().get_model_perms(request)
        return {}

@admin.register(StageAssesment2)
class StageAssesment2Admin(admin.ModelAdmin):
    model = StageAssesment2
    list_display = ('id', 'get_assesment_title', 'score')

    def get_assesment_title(self, obj):
        return f"{obj.assesment.submission_apply.title} - {obj.assesment.submission_apply.team}"
    get_assesment_title.short_description = 'Assesment Title'

    def get_model_perms(self, request):
        """
        Return empty perms dict if user is not superuser, thus hiding the model from admin index.
        """
        if request.user.is_superuser:
            return super().get_model_perms(request)
        return {}
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

