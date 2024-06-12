from django import forms

from apps.pkm.models import PKMProgram



class PeriodForm(forms.Form):
    PERIOD_CHOICES = PKMProgram.objects.values_list('period', 'period').distinct()
    period = forms.ChoiceField(choices=PERIOD_CHOICES, initial=1)