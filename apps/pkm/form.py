from django import forms
from django.forms import ModelForm
from django.core.exceptions import NON_FIELD_ERRORS
from apps.pkm.models import PKMProgram


class PeriodForm(forms.Form):
    PERIOD_CHOICES = PKMProgram.objects.values_list('period', 'period').distinct()
    period = forms.ChoiceField(choices=PERIOD_CHOICES, initial=1)

    def __init__(self, *args, **kwargs):
        super(PeriodForm, self).__init__(*args, **kwargs)
        self.fields['period'].widget.attrs.update({'class': 'form-control'})

class PKMIdeaContributeApplyTeamForm(ModelForm):
    class Meta: 
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "This team has already applied to this idea contribute."
            }
        }