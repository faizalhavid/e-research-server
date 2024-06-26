from os import path
from django import forms
from django.contrib import admin
from django.forms import BaseInlineFormSet, ModelForm, model_to_dict
from django.http import HttpResponseRedirect
from django.shortcuts import render
from apps.account.models import Lecturer
from django.utils.html import format_html
from apps.proposals.models import *
from django.db.models import Count, Max
from import_export import resources
from import_export.admin import ImportExportModelAdmin
import json


@admin.register(LecturerTeamSubmissionApply)
class LecturerTeamSubmissionApplyAdmin(admin.ModelAdmin):
    model = LecturerTeamSubmissionApply
    list_display = ('lecturer', 'submission_information', )

    # def get_form(self, request, obj=None, **kwargs):
    #     form = super().get_form(request, obj, **kwargs)
    #     if obj:
    #         # Filter submission_apply queryset based on the lecturer of the current obj
    #         form.base_fields['submission_apply'].queryset = obj.lecturer.submissionsproposalapply_set.all()
    #     return form

    def submission_information(self, obj):
        submission_info = []
        related_submissions = obj.submission_apply.all()
        for submission in related_submissions:
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
    list_display = ('id', 'submission_information', 'status')
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


from import_export import fields, resources

class DynamicMethodField(fields.Field):
    def __init__(self, dynamic_method, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dynamic_method = dynamic_method

    def get_value(self, obj):
        return self.dynamic_method(obj)
    

class AssessmentReportResource(resources.ModelResource):
    def __init__(self, *args, **kwargs):
        super(AssessmentReportResource, self).__init__(*args, **kwargs)
        self.row_number = 0
        self.dynamic_columns = {}

    stage_2_average_score = fields.Field(column_name='Rata rata nilai')
    stage_2_final_score =  fields.Field(column_name='Jumlah nilai')
    stage_2_comment = fields.Field(column_name='Komentar Reviewer')
    number = fields.Field(column_name='number', attribute=None)
    get_submission_apply_title = fields.Field(attribute='get_submission_apply_title', column_name='Judul PKM')
    get_degree_leader = fields.Field(attribute='get_degree_leader', column_name='Jenjang')
    get_major_leader = fields.Field(attribute='get_major_leader', column_name='Prodi')
    get_final_score = fields.Field(attribute='get_final_score', column_name='Final Score')
    get_leader_info = fields.Field(attribute='get_leader_info', column_name='Nama Ketua - NRP')
    get_reviewer_info = fields.Field(attribute='get_reviewer_info', column_name='Reviewer Info')

    def dehydrate_stage_2_comment(self, assessment_report):
        if assessment_report.assessment_review is None:
            return '-'

    def dehydrate_stage_2_average_score(self, assessment_report):
        return assessment_report.calculate_stage_2_average_score()

    def dehydrate_stage_2_final_score(self, assessment_report):
        if assessment_report.assessment_review is None:
            return '-'
        return assessment_report.assessment_review.final_score    

    def create_dynamic_method(self, assessment):
        def dynamic_method(*args, **kwargs):
            # Return the score of the assessment captured by the closure
            return assessment.score
        return dynamic_method

    def before_export(self, queryset, *args, **kwargs):
        # Iterate through objects to dynamically add stage_assessment_2 columns
        for obj in queryset:
            for assessment in obj.stage_assessment_2.all():  # Iterate over related objects
                key_title = assessment.key_assesment.title
                presentence = assessment.key_assesment.presentase
                column_name = f"{key_title} {presentence}"
                attribute_name = f"dehydrate_stage_assessment_2_{assessment.pk}"

                # Create a dynamic method to fetch score
                setattr(self, attribute_name, self.create_dynamic_method(assessment))
                dynamic_method = self.create_dynamic_method(assessment)
                (dynamic_method)
                # Add dynamic field to fields dictionary
                self.dynamic_columns[column_name] = DynamicMethodField(
                    dynamic_method=dynamic_method,
                    column_name=column_name
                )

        self.fields.update(self.dynamic_columns)
            
   


    # Define methods to get custom field values
    def dehydrate_get_submission_apply_title(self, obj):
        return obj.assessment_submission_proposal.submission_apply.title

    def dehydrate_get_degree_leader(self, obj):
        return obj.assessment_submission_proposal.submission_apply.team.leader.degree

    def dehydrate_get_major_leader(self, obj):
        # Assuming the Major model has a 'name' attribute
        return obj.assessment_submission_proposal.submission_apply.team.leader.major.name

    def dehydrate_get_final_score(self, obj):
        if obj.assessment_review is None or obj.assessment_review.final_score is None:
            return '-'
        return obj.assessment_review.final_score

    def dehydrate_get_leader_info(self, obj):
        leader = obj.assessment_submission_proposal.submission_apply.team.leader
        return f"{leader.full_name} - {leader.nrp}"

    def dehydrate_get_reviewer_info(self, obj):
        lecturer = obj.assessment_submission_proposal.reviewer
        return f"{lecturer.full_name} / {lecturer.phone_number}"

    def dehydrate_number(self, obj):
        self.row_number += 1  # Increment the counter
        return self.row_number

    class Meta:
        model = AssessmentReport
        fields = ('number', 'get_submission_apply_title', 'get_degree_leader', 'get_major_leader', 'get_final_score', 'get_leader_info', 'get_reviewer_info',)
        export_order = ('number', 'get_submission_apply_title','get_leader_info' ,'get_degree_leader', 'get_major_leader', 'get_final_score', 'get_reviewer_info',)
        
        def get_queryset(self):
        # Override this method if you need to filter the records being exported
            return self._meta.model.objects.all()

        # Override import_data to prevent any import operations
        def import_data(self, dataset, dry_run=False, raise_errors=False, use_transactions=None, collect_failed_rows=False, **kwargs):
            raise NotImplementedError("Importing is not allowed")

class CategoryFilter(admin.RelatedFieldListFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = ('Category')

    def choices(self, changelist):
        # Override choices to remove the "All" option
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.lookup_val == str(lookup),
                'query_string': changelist.get_query_string({self.lookup_kwarg: lookup}),
                'display': title,
            }

@admin.register(AssessmentReport)
class AssessmentReportAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = AssessmentReportResource
    list_display = (        
        'get_submission_apply_title', 
        'get_leader_info', 
        'get_degree_leader', 
        'get_major_leader', 
        'get_final_score', 
        'get_reviewer_info',
        'display_stage_2_average_score',  
    )

    change_list_template = 'admin/proposal/assessmentreport/change_list.html'
    list_filter = (
        ('assessment_submission_proposal__submission_apply__category', CategoryFilter),
    )
   
    def changelist_view(self, request, extra_context=None):
        # Ensure the filter is always applied
        if not request.GET.get('assessment_submission_proposal__submission_apply__category__id__exact'):
            # Set the default filter value (replace '1' with the actual default category ID you want)
            default_category_id = 1  # Example category ID
            query_string = request.META['QUERY_STRING']
            if query_string:
                query_string = f"assessment_submission_proposal__submission_apply__category__id__exact={default_category_id}&{query_string}"
            else:
                query_string = f"assessment_submission_proposal__submission_apply__category__id__exact={default_category_id}"
            return HttpResponseRedirect(f"{request.path}?{query_string}")

        extra_context = extra_context or {}
        extra_context['categories'] = AssessmentReport.objects.values_list(
            'assessment_submission_proposal__submission_apply__category__name', flat=True
        ).distinct()
        
        # Customize list display based on active filter category
        self.list_display = self.get_list_display(request)

        return super().changelist_view(request, extra_context=extra_context)



    search_fields = ('assessment_submission_proposal__submission_apply__team__name', 'report_details')
    readonly_fields = ('assessment_submission_proposal', 'stage_assessment_2', 'assessment_review')

    fieldsets = (
        (None, {
            'fields': ('assessment_submission_proposal', 'stage_assessment_2', 'assessment_review',)
        }),
    )
    def display_stage_2_average_score(self, obj):
        return obj.calculate_stage_2_average_score()
    display_stage_2_average_score.short_description = 'Nilai Rata - Rata'
    def get_submission_apply_title(self, obj):
        return obj.assessment_submission_proposal.submission_apply.title
    get_submission_apply_title.short_description = 'Judul PKM'

    def get_degree_leader(self, obj):
        return obj.assessment_submission_proposal.submission_apply.team.leader.degree
    get_degree_leader.short_description = 'Jenjang'

    def get_major_leader(self, obj):
        return obj.assessment_submission_proposal.submission_apply.team.leader.major
    get_major_leader.short_description = 'Prodi'

    def get_final_score(self, obj):
        if obj and hasattr(obj, 'assessment_review') and obj.assessment_review and hasattr(obj.assessment_review, 'final_score'):
            return obj.assessment_review.final_score
        
        return None  # Or return 0 as a default value, depending on your requirements

    def get_assessment_titles(self, obj):
        # Assuming `key_assesment` is a valid field or related manager on the related objects
        # and `title` is a field on the objects returned by `key_assesment`
        return ", ".join([stage_assessment.key_assesment.title for stage_assessment in obj.stage_assessment_2.all()])

    def get_leader_info(self, obj):
        leader = obj.assessment_submission_proposal.submission_apply.team.leader
        return f"{leader.full_name} - {leader.nrp}"
    get_leader_info.short_description = 'Nama Ketua - NRP'

    def get_reviewer_info(self, obj):
        lecturer = obj.assessment_submission_proposal.reviewer
        return f"{lecturer.full_name} / {lecturer.phone_number}"
    get_reviewer_info.short_description = 'Reviewer Info'

    def save_model(self, request, obj, form, change):
        obj.generate_report_details()  
        super().save_model(request, obj, form, change)

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
            'style': 'width:700px;word-wrap: break-word;height:900px!important;padding: 10px 10px!important;'
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
            'style': 'width: 700px;' 
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
        if obj is None:
            return super().get_formset(request, obj, **kwargs)
        key_assesments = KeyStageAssesment2.objects.filter(category=obj.submission_apply.category) if obj.submission_apply.category else KeyStageAssesment2.objects.none()
        key_assesment_count = key_assesments.count()
        self.extra = key_assesment_count if key_assesment_count > 0 else 1
        self.max_num = key_assesment_count
        (key_assesment_count, self.extra, self.max_num)
    
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

class AssesmentReviewForm(forms.ModelForm):
    class Meta:
        model = AssesmentReview
        fields = '__all__'  # Include all fields from the model
        widgets = {
            'final_score': forms.TextInput(attrs={'readonly': 'readonly'}),
            'comment': forms.Textarea(attrs={'rows': 6, 'cols': 40}), 
        }

# Step 2: Integrate the form with the inline admin
class AssesmentReviewInline(admin.TabularInline):
    model = AssesmentReview
    form = AssesmentReviewForm  # Use the custom form
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
                # Debugging:  or log instance to ensure it's correct
                ("Saving instance:", instance)
                instance.save()
            # Save many-to-many fields
            formset.save_m2m()
            super().save_formset(request, form, formset, change)
        else:
            # Debugging:  or log formset errors
            ("Formset is not valid:", formset.errors)

    
    inlines = [StageAssesment1Inline, StageAssesment2Inline, AssesmentReviewInline]
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

    def get_changelist_instance(self, request):
        """
        Override to dynamically set list_editable based on user permissions.
        """
        changelist = super().get_changelist_instance(request)
        if request.user.is_superuser or request.user.groups.filter(name='Admin').exists():
            self.list_editable = ('reviewer',)
        else:
            self.list_editable = ()
        return changelist

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
        (submission)
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
    


    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser or request.user.groups.filter(name='Admin').exists():
            return True
        return False

    def has_add_permission(self, request):
        if request.user.is_superuser or request.user.groups.filter(name='Admin').exists():
            return True
        return False






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

