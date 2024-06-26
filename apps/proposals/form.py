from django import forms


from apps.account.models import Lecturer
from apps.proposals.models import KeyStageAssesment1, StageAssesment1, StageAssesment2, SubmissionsProposalApply

from django.utils.safestring import mark_safe

class AssignForm(forms.Form):
    lecturer = forms.ModelChoiceField(queryset=Lecturer.objects.all())
    submission_apply = forms.ModelChoiceField(queryset=SubmissionsProposalApply.objects.filter(status='APPLIED'))


        
# class StageAssesment1Form(forms.ModelForm):
#     class Meta:
#         model = StageAssesment1
#         fields = ['key_assesment', 'status']

# class StageAssesment1InlineFormSet(forms.BaseInlineFormSet):
#     def add_fields(self, form, index):
#         super().add_fields(form, index)
#         form.fields['key_assesment'].widget.attrs['readonly'] = True

class StageAssesment2Form(forms.ModelForm):
    class Meta:
        model = StageAssesment2
        fields = '__all__'
        widgets = {
            'key_assessment': forms.CheckboxSelectMultiple,
            'score': forms.Select,  
        }


class AssignLecturerForm(forms.Form):
    lecturer = forms.ModelChoiceField(queryset=Lecturer.objects.all(), required=True, label='Choose Lecturer')
    proposals = forms.ModelMultipleChoiceField(queryset=SubmissionsProposalApply.objects.filter(status='APPLIED'), required=True, label='Choose Proposal')
