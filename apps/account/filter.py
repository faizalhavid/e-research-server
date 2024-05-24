
from django.contrib.auth.models import Group
import django_filters

from apps.account.models import Lecturer, Student, User

class UserFilter(django_filters.FilterSet):
    groups = django_filters.ModelChoiceFilter(queryset=Group.objects.all(), to_field_name='name')

    class Meta:
        model = User
        fields = ['groups']

class StudentFilter(django_filters.FilterSet):
    nrp = django_filters.CharFilter(lookup_expr='exact')
    full_name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Student
        fields = ['nrp', 'full_name']
        
class LecturerFilter(django_filters.FilterSet):
    nidn = django_filters.CharFilter(lookup_expr='exact')
    full_name = django_filters.CharFilter(lookup_expr='icontains')
    group = django_filters.ModelChoiceFilter(queryset=Group.objects.all(), to_field_name='name')
    class Meta:
        model = Lecturer
        fields = ['nidn', 'full_name', 'group']