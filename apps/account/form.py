from django import forms
from proposals.models import PKMProgram


class PeriodForm(forms.Form):
    PERIOD_CHOICES = PKMProgram.objects.values_list('period', 'name')
    period = forms.ChoiceField(choices=PERIOD_CHOICES, initial=1)