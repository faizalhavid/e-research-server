from django.contrib import admin
from apps.account.models import *
from django.contrib.auth import get_user_model
from django.contrib.admin.models import LogEntry
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from django.utils import timezone
from django.contrib.admin import SimpleListFilter
from django.contrib.auth.hashers import make_password
from taggit.models import Tag
from django.utils.html import format_html

from apps.proposals.models import SubmissionsProposalApply


class StudentInline(admin.StackedInline):
    model = Student

    # def has_add_permission(self, request, obj=None):
    #     if obj == request.user:
    #         return False
    #     return super().has_add_permission(request, obj)

    # def has_change_permission(self, request, obj=None):
    #     if request.user.is_superuser:
    #         return True
    #     return False
class LecturerInline(admin.StackedInline):
    model = Lecturer

    # def has_add_permission(self, request, obj=None):
    #     if obj == request.user:
    #         return False
    #     return super().has_add_permission(request, obj)

    # def has_change_permission(self, request, obj=None):
    #     if request.user.is_superuser:
    #         return True
    #     return False
class StudentModelResource(resources.ModelResource):
    class Meta:
        model = Student
        fields = ('nrp', 'full_name', 'admission_year', 'degree', 'major', 'department')
        export_order = ('nrp', 'full_name', 'admission_year', 'degree', 'major', 'department')
        import_id_fields = ['nrp']
        import_field_names = {
            'NRP': 'nrp',
            'FULL_NAME': 'full_name',
            'ADMISSION_YEAR': 'admission_year',
            'DEGREE': 'degree',
            'MAJOR': 'major',
            'DEPARTMENT': 'department'
        }
    def dehydrate_major(self, student):
        if student.major is not None:
            return student.major.name  # Assuming 'name' is a field in the Major model
        else:
            return ''

    def dehydrate_department(self, student):
        if student.department is not None:
            return student.department.name  # Assuming 'name' is a field in the Department model
        else:
            return ''

    def get_export_headers(self):
        headers = super().get_export_headers()
        new_headers = []
        for header in headers:
            if header == 'full_name':
                new_headers.append('Nama Mahasiswa')
            elif header == 'nrp':
                new_headers.append('NRP')
            elif header == 'admission_year':
                new_headers.append('Tahun Masuk')
            elif header == 'degree':
                new_headers.append('Jenjang')
            elif header == 'major':
                new_headers.append('Prodi')
            elif header == 'department':
                new_headers.append('Departemen')
            else:
                new_headers.append(header)
        return new_headers
    def before_import_row(self, row, row_number=None, **kwargs):
        row['nrp'] = row.pop('NRP')
        row['full_name'] = row.pop('Nama Mahasiswa')
        row['admission_year'] = row.pop('Tahun Masuk')
        row['degree'] = row.pop('Jenjang')
        major_name = row.pop('Prodi')
        major = Major.objects.get(name=major_name)  # Assuming 'name' is a unique field in the Major model
        row['major'] = major.id

        department_name = row.pop('Departemen')
        department = Departement.objects.get(name=department_name)  # Assuming 'name' is a unique field in the Department model
        row['department'] = department.id
        return row

@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ('id','full_name', 'agency')
    search_fields = ('id','full_name', 'agency')
    list_per_page = 15
    ordering = ('full_name',)
    readonly_fields = ('guest_image',)



    def guest_image(self, obj):
        if obj.image and hasattr(obj.image, 'url'):
            return format_html('<img src="{}" width="80" height="80" />'.format(obj.image.url))
        else:
            return format_html('<div style="width:80px;height:80px;background-color:#f0f0f0;color:#999999;font-size:12px;text-align:center;line-height:80px;">No Image</div>')
    
@admin.register(Student)
class StudentAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    resource_class = StudentModelResource
    list_display = ( 'nrp','full_name', 'department', 'major', 'degree', 'admission_year')
    search_fields = ('full_name', 'nrp')
    list_display_links = ('nrp', 'full_name')
    list_filter= ('major', 'department', 'degree', 'admission_year')
    list_per_page = 15
    ordering = ('admission_year', 'full_name')
    readonly_fields = ('student_image',)
    fieldsets = (
        (None, {
            'fields': ('nrp', 'full_name', 'department', 'major', 'degree', 'admission_year','image' ,'student_image')
        }),
    )

    def student_image(self, obj):
        if obj.image and hasattr(obj.image, 'url'):
            return format_html('<img src="{}" width="80" height="80" />'.format(obj.image.url))
        else:
            return format_html('<div style="width:80px;height:80px;background-color:#f0f0f0;color:#999999;font-size:12px;text-align:center;line-height:80px;">No Image</div>')
    
def make_lecturer_reviewer(self, request, queryset):
    group = Group.objects.get(name='LecturerReviewer')
    for obj in queryset:
        obj.user.groups.add(group)
make_lecturer_reviewer.short_description = "Make selected lecturers reviewers"

def remove_lecturer_reviewer(self, request, queryset):
    group = Group.objects.get(name='LecturerReviewer')
    for obj in queryset:
        obj.user.groups.remove(group)
remove_lecturer_reviewer.short_description = "Remove reviewer status from selected lecturers"


class LecturerReviewerStatusFilter(SimpleListFilter):
    title = 'Reviewer Status'
    parameter_name = 'reviewer_status'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Yes'),
            ('no', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(user__groups__name='LecturerReviewer')
        elif self.value() == 'no':
            return queryset.exclude(user__groups__name='LecturerReviewer')    


class LecturerModelResource(resources.ModelResource):
    user_email = fields.Field(attribute='user', column_name='user.email')
    class Meta:
        model = Lecturer
        fields = ('nidn', 'full_name', 'department')  # Add or remove fields as needed
        export_order = ('nidn', 'full_name', 'department')  # Add or remove fields as needed
        import_id_fields = ['nidn']
        import_field_names = {
            'ID': 'id',
            'FULL_NAME': 'full_name',
            'DEPARTMENT': 'department'
        }

    def dehydrate_user_email(self, lecturer):
        return lecturer.user.email if lecturer.user else ''

    def dehydrate_department(self, lecturer):
        if lecturer.department is not None:
            return lecturer.department.name  # Assuming 'name' is a field in the Department model
        else:
            return ''

    def get_export_headers(self):
        headers = super().get_export_headers()
        new_headers = []
        for header in headers:
            if header == 'full_name':
                new_headers.append('Nama Dosen')
            elif header == 'nidn':
                new_headers.append('NIDN')
            elif header == 'department':
                new_headers.append('Departemen')
            else:
                new_headers.append(header)
        return new_headers

    def before_import_row(self, row, row_number=None, **kwargs):
        row['nidn'] = row.pop('NIDN')
        row['full_name'] = row.pop('Nama Dosen')
        department_name = row.pop('Departemen')
        department = Departement.objects.get(name=department_name)  # Assuming 'name' is a unique field in the Department model
        row['department'] = department.id
        return row


@admin.register(Lecturer)
class LecturerAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = LecturerModelResource
    list_display = ('nidn', 'full_name', 'department', 'get_count_be_lecturer_supervisor', 'lecturer_reviewer_status')
    list_display_links = ('nidn', 'full_name')
    search_fields = ('full_name', 'nidn')
    list_display_links = ('nidn', 'full_name')
    list_filter = ['department', LecturerReviewerStatusFilter]
    list_per_page = 15
    ordering = ('full_name', 'department')
    readonly_fields = ('lecturer_image','get_count_be_lecturer_supervisor', 'lecturer_reviewer_status')
    fieldsets = (
        (None, {
            'fields': ('nidn', 'full_name', 'department', 'image', 'lecturer_image','user')
        }),
    )
    actions = [make_lecturer_reviewer, remove_lecturer_reviewer]
    

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.groups.filter(name='LecturerReviewer').exists():
            return qs.filter(user=request.user)
        return qs
    
    def get_count_be_lecturer_supervisor(self, obj):
        count = SubmissionsProposalApply.objects.filter(team__lecturer=obj).count()
        if count > 10:
            return format_html('<span style="color: red;">{}</span>', count)
        else:
            return count
    get_count_be_lecturer_supervisor.short_description = 'Jumlah Team yang di bimbing'

    
    def lecturer_reviewer_status(self, obj):
        if obj.user and obj.user.groups.filter(name='LecturerReviewer').exists():
            return format_html('<span style="color: green;">&#10004;</span>')  # Checkmark
        else:
            return format_html('<span style="color: red;">&#10060;</span>')  # Cross
    lecturer_reviewer_status.short_description = 'Reviewer Status'

    def lecturer_image(self, obj):
        if obj.image and hasattr(obj.image, 'url'):
            return format_html('<img src="{}" width="80" height="80" />'.format(obj.image.url))
        else:
            return format_html('<div style="width:80px;height:80px;background-color:#f0f0f0;color:#999999;font-size:12px;text-align:center;line-height:80px;">No Image</div>')
    
User = get_user_model()

class UserModelResource(resources.ModelResource):
    class Meta:
        model = User
        fields = ('email', 'groups')
        export_order = ('email', 'groups')
        import_id_fields = ['email']
        import_field_names = {
            'EMAIL': 'email',
            'PASSWORD': 'password',
            'GROUPS': 'groups',
        }
        

    def get_export_headers(self):
        headers = super().get_export_headers()
        new_headers = []
        for header in headers:
            if header == 'email':
                new_headers.append('Email')
            elif header == 'groups':
                new_headers.append('User Groups')
            else:
                new_headers.append(header)
        return new_headers

    def before_import_row(self, row, row_number=None, **kwargs):
        row['email'] = row.pop('Email')
        row['groups'] = row.pop('User Groups')
        if 'Password' in row:
            row['password'] = make_password(row.pop('Password'))
        return row

@admin.register(User)
class UserAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = UserModelResource
    readonly_fields = ('log_entries','online_status','user_role')
    list_per_page = 15
    list_display_links = ['id','email']
    list_display = ('id','email','user_role','online_status')
    search_fields = ('email', 'first_name', 'last_name')
    # for debug
    inlines = [StudentInline, LecturerInline]
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions')

    def save_model(self, request, obj, form, change):
        # If the password was changed, update it
        if 'password' in form.changed_data:
            obj.set_password(obj.password)
        super().save_model(request, obj, form, change)
        # If the user is not a superuser, remove the is_superuser flag
        if not request.user.is_superuser:
            obj.is_superuser = False
        super().save_model(request, obj, form, change)
        # If the staff created a user, make it active
        if not change: 
            if request.user.is_staff:
                obj.is_active = True
        super().save_model(request, obj, form, change)

    def log_entries(self, obj):
        return "\n".join(
            f"{entry.action_time} {entry.get_action_flag_display()}: {entry.object_repr}"
            for entry in LogEntry.objects.filter(user=obj).order_by('-action_time')[:6]
        )
    log_entries.short_description = 'Log entries'

    def online_status(self, obj):
        if obj.last_activity is not None:
            return obj.last_activity >= timezone.now() - timezone.timedelta(minutes=5)
        else:
            return False
    online_status.boolean = True
    online_status.short_description = 'Online'


    def get_fieldsets(self, request, obj=None):
        # Base fieldsets without the 'password' field
        fieldsets = [
            ('Account', {'fields': ('email', 'user_role')}),
            ('Personal info', {'fields': ('first_name', 'last_name')}),
        ]
        
        # Check if the user is a superuser, in the "Admin" group, or is editing their own account
        if request.user.is_superuser or request.user.groups.filter(name="Admin").exists() or (obj and obj == request.user):
            # Include the 'password' field for these users
            fieldsets[0][1]['fields'] = ('email', 'password', 'user_role')
        
        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        user = request.user
        # Check if the user is not a superuser and not in the "Admin" group
        if not user.is_superuser and not Group.objects.get(name="Admin").user_set.filter(id=user.id).exists():
            return readonly_fields + ('Student', 'Lecturer', 'is_superuser', 'is_active', 'last_login', 'date_joined')
        return readonly_fields
        
    
    def user_role(self, obj):
        if hasattr(obj, 'user_profile'):
            if hasattr(obj.user_profile, 'student'):
                return f"Student ({obj.user_profile.student.full_name} - {obj.user_profile.student.nrp})"
            elif hasattr(obj.user_profile, 'lecturer'):
                return f"Lecturer ({obj.user_profile.lecturer.full_name} - {obj.user_profile.lecturer.nidn})"
        if obj.is_superuser:
            return "Superuser"
        if obj.groups.filter(name='Admin').exists():
            return "Admin"
        return ""
    user_role.short_description = 'User Role'
    def get_model_perms(self, request):
        """
        Return empty perms dict if user is not superuser, thus hiding the model from admin index.
        """
        if request.user.is_superuser or Group.objects.get(name="Admin").user_set.filter(id=request.user.id).exists():
            return super().get_model_perms(request)
        return {}
    
    def has_add_permission(self, request):
        # Allow adding if the user is a superuser or in the "Admin" group
        return request.user.is_superuser or request.user.groups.filter(name='Admin').exists()

    def has_change_permission(self, request, obj=None):
        # Allow changing if no specific object is targeted (e.g., accessing the list view)
        if obj is None:
            return True
        # Allow if the user is a superuser, in the "Admin" group, or editing their own profile
        return request.user.is_superuser or request.user.groups.filter(name='Admin').exists() or obj == request.user

    def has_delete_permission(self, request, obj=None):
        # Allow deleting if no specific object is targeted (e.g., accessing the list view)
        if obj is None:
            return True
        # Allow if the user is a superuser, in the "Admin" group, or deleting their own account
        return request.user.is_superuser or request.user.groups.filter(name='Admin').exists() or obj == request.user

    def get_readonly_fields(self, request, obj=None):
        # Make all fields read-only for users who are not superusers, not in the "Admin" group, and not editing their own profile
        if not request.user.is_superuser and not request.user.groups.filter(name='Admin').exists() and (obj is None or obj != request.user):
            return self.fields or [f.name for f in self.model._meta.fields]
        return super().get_readonly_fields(request, obj)
    
@admin.register(Departement)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ( 'name','abbreviation', 'display_majors')
    search_fields = ('name', )

    def display_majors(self, obj):
        return ", ".join(major.name for major in obj.majors.all())
    display_majors.short_description = 'Majors'
    

@admin.register(Major)
class MajorAdmin(admin.ModelAdmin):
    list_display = ( 'name','abbreviation', 'total_student')
    
    def total_student(self, obj):
        return Student.objects.filter(major=obj).count()
    



